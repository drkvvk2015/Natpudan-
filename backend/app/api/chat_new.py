"""Chat API endpoints with database and OpenAI integration."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from app.database import get_db
from app.api.auth_new import get_current_user
from app.models import User
from app.crud import (
    create_conversation,
    get_user_conversations,
    get_conversation,
    delete_conversation,
    create_message,
    get_conversation_messages,
)
from app.utils.ai_service import generate_ai_response
import os

# Knowledge base is NOT loaded at import time to avoid blocking
# It will be loaded on first use
_knowledge_base = None
_kb_load_attempted = False

# Visual content service - lazy loaded
_visual_service = None

def _get_visual_service():
    """Lazy load visual content service"""
    global _visual_service
    if _visual_service is None:
        try:
            from app.services.visual_content_service import MedicalVisualContentService
            _visual_service = MedicalVisualContentService()
            logger.info("Visual content service loaded successfully")
        except Exception as e:
            logger.warning(f"Visual content service not available: {e}")
            return None
    return _visual_service

def _get_kb():
    """Lazy load knowledge base - returns None if unavailable"""
    global _knowledge_base, _kb_load_attempted
    
    if not _kb_load_attempted:
        _kb_load_attempted = True
        try:
            from app.services.enhanced_knowledge_base import get_knowledge_base
            _knowledge_base = get_knowledge_base()
            logger.info("Knowledge base loaded successfully")
        except Exception as e:
            logger.warning(f"Knowledge base not available: {e}")
            _knowledge_base = None
    
    return _knowledge_base

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: str


class ChatMessageResponse(BaseModel):
    message: ChatMessage
    conversation_id: int


class Conversation(BaseModel):
    id: int
    title: Optional[str]
    created_at: str
    updated_at: str
    message_count: int


class ConversationDetails(BaseModel):
    id: int
    title: Optional[str]
    created_at: str
    updated_at: str
    messages: List[ChatMessage]


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a chat message and get AI response."""
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = get_conversation(db, request.conversation_id, current_user.id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation with title from first message
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation = create_conversation(db, current_user.id, title)
        
        # Save user message
        create_message(
            db=db,
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )
        
        # Get conversation history for context
        messages = get_conversation_messages(db, conversation.id)
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Search knowledge base for relevant medical information
        search_results = []
        knowledge_context = ""
        detailed_sources = []
        
        try:
            # Get knowledge base and search for relevant content
            kb = _get_kb()
            if kb is None:
                logger.info("Knowledge base not available, skipping search")
            else:
                # Search for MORE results to provide comprehensive information
                search_results = kb.search(request.message, top_k=10)  # Increased to 10 for detailed context
            
                if search_results:
                    knowledge_context = "\n\n[BOOKS] **Medical Knowledge Base - Detailed References:**\n\n"
                    
                    for i, result in enumerate(search_results, 1):
                        # Get FULL text (up to 2000 chars for detailed context)
                        text_content = result['text'][:2000]
                        if len(result['text']) > 2000:
                            text_content += "... [truncated]"
                        
                        source_name = result.get('source', 'Medical Database')
                        relevance = result.get('score', 0)
                        knowledge_source = result.get('knowledge_source', 'Local Database')
                        
                        # Extract document_id for reference links (now at top level)
                        doc_id = result.get('document_id', None)
                        chunk_id = result.get('chunk_id', None)
                        page_num = result.get('page_number', None)
                        
                        # Build clickable reference link
                        ref_link = ""
                        if doc_id:
                            # Local database document with viewable content
                            ref_link = f"  [View Document](/api/medical/knowledge/documents/{doc_id})"
                        elif 'pubmed' in source_name.lower() or 'pmid' in str(result.get('metadata', {})):
                            # PubMed article - link to external source
                            pmid = result.get('metadata', {}).get('pmid', None)
                            if pmid:
                                ref_link = f"  [PubMed Article](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)"
                        elif 'http' in source_name.lower() or result.get('url'):
                            # External URL source
                            url = result.get('url', source_name)
                            ref_link = f"  [Source]({url})"
                        
                        # Build detailed source entry with clickable link
                        knowledge_context += f"### Reference [{i}] - {source_name}{ref_link}\n"
                        knowledge_context += f"**Source Type:** {knowledge_source} | **Relevance:** {relevance:.2f}"
                        if page_num:
                            knowledge_context += f" | **Page:** {page_num}"
                        knowledge_context += "\n\n"
                        knowledge_context += f"**Content:**\n{text_content}\n\n"
                        knowledge_context += "---\n\n"
                        
                        # Track sources for citation with links
                        source_entry = {
                            "number": i,
                            "source": source_name,
                            "type": knowledge_source,
                            "relevance": f"{relevance:.2f}",
                            "excerpt": result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
                        }
                        if doc_id:
                            source_entry['link'] = f"/api/medical/knowledge/documents/{doc_id}"
                            source_entry['link_text'] = "View Document"
                        detailed_sources.append(source_entry)
                    
                    logger.info(f"Found {len(search_results)} relevant results from knowledge base")
                else:
                    logger.info("No relevant results found in knowledge base")
        except Exception as e:
            logger.warning(f"Knowledge base search failed: {e}")
            # Continue without KB data
        
        # Try to generate AI response with OpenAI (optional enhancement)
        ai_response = ""
        openai_available = False
        
        # First, check if we have knowledge base results
        if search_results:
            # We have local knowledge - this is our primary source!
            
            # Build sources list for citation with clickable links
            sources_list = "\n".join([
                f"  [{s['number']}] {s['source']} ({s['type']}) - Relevance: {s['relevance']}" +
                (f"  [View]({s['link']})" if s.get('link') else "")
                for s in detailed_sources
            ])
            
            # Get visual resources (images and videos)
            visual_content = ""
            try:
                logger.info("Attempting to load visual service...")
                visual_service = _get_visual_service()
                logger.info(f"Visual service loaded: {visual_service is not None}")
                
                if visual_service:
                    # Extract medical condition from query or first high-relevance result
                    medical_condition = None
                    if search_results and len(search_results) > 0:
                        logger.info(f"Processing {len(search_results)} search results for medical condition extraction")
                        # Try to extract condition from the result content
                        import re
                        first_result = search_results[0]
                        content = first_result.get('text', '') or first_result.get('content', '')
                        logger.info(f"First result content preview: {content[:200]}")
                        
                        # Look for condition name in markdown headers like "**Pneumonia** (ICD-10: J18)"
                        condition_match = re.search(r'\*\*([^*]+)\*\*.*?\(ICD-10:', content)
                        if condition_match:
                            medical_condition = condition_match.group(1).strip()
                            logger.info(f"[OK] Extracted medical condition from KB: '{medical_condition}'")
                        else:
                            # Fallback: use the original query
                            medical_condition = request.message
                            logger.info(f"Using query as medical condition: '{medical_condition}'")
                    else:
                        medical_condition = request.message
                        logger.info(f"No search results, using query: '{medical_condition}'")
                    
                    logger.info(f"Getting visual resources for: '{medical_condition}'")
                    visual_resources = visual_service.get_visual_resources(
                        request.message,
                        medical_condition=medical_condition
                    )
                    logger.info(f"Visual resources returned: {len(visual_resources.get('images', []))} images, {len(visual_resources.get('videos', []))} videos")
                    
                    visual_content = visual_service.format_visual_resources_markdown(visual_resources)
                    logger.info(f"[OK] Visual content formatted: {len(visual_content)} characters")
                else:
                    logger.warning("Visual service is None")
            except Exception as e:
                logger.error(f"[ERROR] Could not add visual resources: {e}", exc_info=True)
            
            # Try to enhance with OpenAI for CONSOLIDATED response
            try:
                # NEW: Enhanced prompt for consolidated synthesis
                consolidated_prompt = f"""You are an expert medical AI assistant. Your task is to synthesize information from ALL provided references into ONE comprehensive, flowing narrative.

**User Query:** "{request.message}"

**Medical Knowledge Base References ({len(search_results)} sources):**
{knowledge_context}

**YOUR TASK - CREATE A CONSOLIDATED RESPONSE:**

First, DIRECTLY ANSWER the user's question in the opening paragraph. If they ask "what is fever?" start with a clear definition. Then expand with comprehensive details.

Write a SINGLE, UNIFIED clinical response that synthesizes ALL {len(search_results)} references into one coherent narrative. DO NOT list references separately - instead, INTEGRATE the information seamlessly.

**IMPORTANT:** 
- For definition questions (what is..., define...), START with a clear 2-3 sentence definition
- For clinical questions, START with the most relevant answer
- Then provide comprehensive details organized by sections below

**Required Structure:**

## DIRECT ANSWER
(START HERE: 1-2 paragraphs directly answering the user's specific question)
- If they ask "what is X?" → Define X clearly first
- If they ask "how to treat Y?" → State treatment approach first
- If they ask "what causes Z?" → Explain causes first
[Then continue with comprehensive details below]

## [TARGET] CLINICAL OVERVIEW
(2-3 paragraphs synthesizing key information from all references)
- Definition and significance (expand on direct answer)
- Epidemiology and prevalence
- Primary mechanisms/pathophysiology
[Cite sources throughout: [1], [2], [3], etc.]

##  PATHOPHYSIOLOGY & MECHANISMS
(Consolidated explanation from all references)
- Underlying biological processes
- Disease progression and timeline
- Risk factors and predisposing conditions
[Integrate information from multiple sources]

##  CLINICAL PRESENTATION
(Unified description from all references)
- Common signs and symptoms
- Physical examination findings
- Diagnostic criteria and classifications
- Differential diagnoses
[Synthesize across all sources]

##  DIAGNOSTIC APPROACH
(Evidence-based workup from references)
- Initial assessment and history
- Laboratory and imaging studies
- Diagnostic algorithms
- When to order specific tests
[Combine recommendations from all sources]

## [MED] TREATMENT & MANAGEMENT
(Comprehensive approach from all references)
- First-line therapies (cite evidence [1][2])
- Alternative and adjunctive treatments
- Dosing, administration, monitoring
- Management of complications
- Surgical/procedural interventions (if applicable)
[Integrate treatment strategies from multiple sources]

##  PATIENT CARE & COUNSELING
(Practical guidance from references)
- Patient education points
- Warning signs requiring immediate attention
- Lifestyle modifications
- Follow-up recommendations
- Prognosis and expected outcomes
[Synthesize patient-centered information]

## [WARNING] SPECIAL CONSIDERATIONS
(Important caveats from references)
- Contraindications and precautions
- Special populations (pediatric, geriatric, pregnant)
- Drug interactions and adverse effects
- When to consult specialists
[Consolidate safety information]

**CRITICAL INSTRUCTIONS:**
[OK] SYNTHESIZE - Don't just list facts, create a flowing narrative
[OK] CITE FREQUENTLY - Use [1], [2], [3] throughout (not just at end)
[OK] INTEGRATE - Combine information from multiple sources into single statements
[OK] BE COMPREHENSIVE - Use information from ALL {len(search_results)} references
[OK] BE SPECIFIC - Include dosages, values, criteria when available
[OK] BE CLINICAL - Write for healthcare professionals making decisions
[OK] CONSOLIDATE - One unified answer, not separate summaries per reference

**Example of GOOD synthesis:**
"The condition affects 5-10% of adults [1] with higher prevalence in men over 50 [2][3]. Initial presentation typically includes symptom X [1][4] and finding Y [2], which helps differentiate it from condition Z [3]."

**Example of BAD approach:**
"Reference [1] says X. Reference [2] says Y. Reference [3] says Z." [ERROR]

Write as if explaining to a colleague - authoritative, detailed, evidence-based, and actionable."""

                ai_synthesis = await generate_ai_response(
                    messages=conversation_history,
                    system_prompt=consolidated_prompt,
                )
                
                # Format final response with consolidated answer FIRST, then references
                ai_response = f""" **CONSOLIDATED CLINICAL RESPONSE**

[STATS] **Query:** "{request.message}"
[BOOKS] **Synthesized from:** {len(search_results)} medical references

{ai_synthesis}

---

##  COMPLETE REFERENCE LIBRARY

Below are ALL {len(search_results)} sources used in this response. Click any link to view the full document:

"""
                # Add organized references with clickable links
                for i, source in enumerate(detailed_sources, 1):
                    ai_response += f"### [{i}] {source['source']}\n"
                    ai_response += f"**Type:** {source['type']} | **Relevance:** {source['relevance']}\n"
                    if source.get('link'):
                        ai_response += f"**[DOC] [View Full Document]({source['link']})**\n"
                    ai_response += f"\n**Excerpt:** {source['excerpt']}\n\n"
                
                ai_response += f"""{visual_content}

---

## [WARNING] IMPORTANT DISCLAIMER

This consolidated response synthesizes information from {len(search_results)} medical references and should be used alongside:

[OK] Current clinical practice guidelines  
[OK] Patient-specific factors and history  
[OK] Institutional protocols and policies  
[OK] Specialist consultation when indicated  
[OK] Your professional clinical judgment  

 **For medical emergencies, call emergency services immediately (911 in US)**

[TIP] **All sources are clickable** - Review full documents for complete context and additional details."""
                
                openai_available = True
                logger.info(f"[OK] Consolidated response generated from {len(search_results)} references")
            except Exception as e:
                logger.warning(f"OpenAI unavailable, creating structured KB summary: {e}")
                
                # Fallback: Create well-organized response from KB content without OpenAI
                ai_response = f""" **MEDICAL KNOWLEDGE BASE RESULTS**

[STATS] **Query:** "{request.message}"
[BOOKS] **Found:** {len(search_results)} relevant medical references

## [INFO] ORGANIZED REFERENCE SUMMARY

Below is information from our medical knowledge base, organized by relevance. Each reference includes clickable links to full documents.

"""
                # Add each reference in organized format
                for i, source in enumerate(detailed_sources, 1):
                    result = search_results[i-1]
                    text_preview = result['text'][:1500]
                    if len(result['text']) > 1500:
                        text_preview += "... [continued in full document]"
                    
                    ai_response += f"""### [DOC] Reference [{i}] - {source['source']}

**Relevance Score:** {source['relevance']} | **Type:** {source['type']}
"""
                    if source.get('link'):
                        ai_response += f"** [View Full Document]({source['link']})**\n"
                    
                    ai_response += f"""
**Content Preview:**

{text_preview}

---

"""
                
                ai_response += f"""{visual_content}

## [TARGET] HOW TO USE THESE REFERENCES

1. **Review by Relevance** - References are ranked by relevance to your query
2. **Click Links** - Access full documents for complete information
3. **Cross-Reference** - Compare information across multiple sources
4. **Clinical Context** - Apply findings to your specific patient situation
5. **Guidelines** - Verify with current clinical practice standards

## [WARNING] IMPORTANT REMINDERS

[OK] All {len(search_results)} references from verified medical literature  
[OK] Click document links for full clinical context  
[OK] Verify with current practice guidelines  
[OK] Consider patient-specific factors  
[OK] Consult specialists for complex cases  
[OK] Seek immediate care for emergencies  

 **For urgent medical concerns, call emergency services immediately**"""
        else:
            # No knowledge base results - try OpenAI with enhanced medical prompt
            try:
                enhanced_medical_prompt = f"""You are an expert medical AI assistant with comprehensive medical knowledge. Provide detailed, accurate medical information for healthcare professionals.

**User Query:** "{request.message}"

**Your Task:**
Provide a comprehensive, professional medical response covering:

1. **DEFINITION & OVERVIEW** - Clear explanation of the condition/topic
2. **PATHOPHYSIOLOGY** - Underlying mechanisms and biology
3. **CLINICAL PRESENTATION** - Signs, symptoms, and physical findings
4. **DIAGNOSIS** - Diagnostic criteria, tests, and workup
5. **TREATMENT** - Evidence-based management strategies with specifics
6. **PROGNOSIS** - Expected outcomes and complications
7. **PATIENT EDUCATION** - Key counseling points

**Guidelines:**
- Be thorough and clinically detailed
- Include specific values, criteria, and dosages when relevant
- Use medical terminology appropriately
- Cite evidence levels when possible (e.g., "per guidelines...")
- Emphasize clinical decision-making
- Include warning signs and red flags
- Note when specialist consultation is needed

**Format:**
Use clear markdown headers (##) and bullet points for readability. Make it comprehensive enough for clinical decision support.

**Safety Note:**
Always end with appropriate safety reminders about emergencies."""

                ai_response = await generate_ai_response(
                    messages=conversation_history,
                    system_prompt=enhanced_medical_prompt,
                )
                openai_available = True
                logger.info("Response from OpenAI with enhanced medical prompt (no KB results)")
            except Exception as e:
                logger.warning(f"Both KB and OpenAI unavailable: {e}")
                ai_response = f"""I apologize, but I couldn't find specific information about your query in our medical knowledge base.

[INFO] **Your Question:** {request.message}

[TIP] **Suggestions:**
1. Rephrase your question with more specific medical terms
2. Check the knowledge base section to upload relevant medical literature
3. Consult clinical guidelines or medical references directly

[WARNING] For urgent medical concerns, please:
- Consult with a healthcare professional directly
2. Call emergency services if urgent (911 in US)
3. Visit your nearest healthcare facility

The system will be back online shortly."""
        
        # Save AI response and capture created message
        assistant_msg = create_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
        )

        return ChatMessageResponse(
            message=ChatMessage(
                role=assistant_msg.role,
                content=assistant_msg.content,
                created_at=assistant_msg.created_at.isoformat(),
            ),
            conversation_id=conversation.id,
        )
        
    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/history", response_model=List[Conversation])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all conversations for the current user."""
    conversations = get_user_conversations(db, current_user.id)
    
    return [
        Conversation(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
            message_count=len(conv.messages),
        )
        for conv in conversations
    ]


@router.get("/history/{conversation_id}", response_model=ConversationDetails)
async def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific conversation with all messages."""
    conversation = get_conversation(db, conversation_id, current_user.id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = get_conversation_messages(db, conversation_id)
    
    return ConversationDetails(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        messages=[
            ChatMessage(
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat(),
            )
            for msg in messages
        ],
    )


@router.delete("/history/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a conversation."""
    success = delete_conversation(db, conversation_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {"message": "Conversation deleted successfully"}
