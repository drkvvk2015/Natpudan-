"""Streaming chat endpoint for real-time medical responses."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import json
import logging
from sqlalchemy.orm import Session
from typing import AsyncGenerator

from app.database import get_db
from app.api.auth_new import get_current_user
from app.models import User
from app.crud import create_conversation, create_message, get_conversation, get_conversation_messages
from app.utils.ai_service import generate_ai_response_stream

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message/stream")
async def send_message_stream(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stream chat message response in real-time using Server-Sent Events (SSE)."""
    message_content = request.get("message", "")
    conversation_id = request.get("conversation_id")

    if not message_content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    try:
        # Get or create conversation
        if conversation_id:
            conversation = get_conversation(db, conversation_id, current_user.id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            title = message_content[:50] + "..." if len(message_content) > 50 else message_content
            conversation = create_conversation(db, current_user.id, title)

        # Save user message
        create_message(
            db=db,
            conversation_id=conversation.id,
            role="user",
            content=message_content,
        )

        # Get conversation history
        messages = get_conversation_messages(db, conversation.id)
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Stream the response
        async def generate():
            accumulated_response = ""
            try:
                # Get knowledge base context
                kb = None
                try:
                    from app.services.enhanced_knowledge_base import get_knowledge_base
                    kb = get_knowledge_base()
                except:
                    logger.warning("Knowledge base not available for streaming")

                # Search KB if available
                search_results = []
                if kb:
                    search_results = kb.search(message_content, top_k=5)

                # Build context
                knowledge_context = ""
                if search_results:
                    knowledge_context = "\n\n[MEDICAL_KB_SOURCES]\n"
                    for i, result in enumerate(search_results, 1):
                        knowledge_context += f"\n## Reference [{i}]\n"
                        knowledge_context += f"Source: {result.get('source', 'Unknown')}\n"
                        knowledge_context += f"Content: {result['text'][:500]}...\n"

                # Medical system prompt
                system_prompt = f"""You are an expert medical AI assistant. Provide evidence-based medical information.

{knowledge_context if knowledge_context else ''}

Respond in clear markdown format with:
- Definition/Overview
- Key symptoms/signs
- Diagnostic approach
- Treatment options
- When to seek emergency care
- Sources and references

Be thorough, specific, and cite evidence."""

                # Stream response from LLM
                async for chunk in generate_ai_response_stream(
                    messages=conversation_history,
                    system_prompt=system_prompt,
                ):
                    accumulated_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk, 'type': 'content'})}\n\n"

                # Save full response to database
                create_message(
                    db=db,
                    conversation_id=conversation.id,
                    role="assistant",
                    content=accumulated_response,
                )

                # Send completion signal
                yield f"data: {json.dumps({'type': 'complete', 'conversation_id': conversation.id})}\n\n"

            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in streaming chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process stream: {str(e)}"
        )
