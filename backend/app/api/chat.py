"""Chat API endpoints for AI Medical Assistant conversations."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory storage (replace with database in production)
conversations_db: Dict[int, Dict[str, Any]] = {}
next_conversation_id = 1
next_message_id = 1


class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatMessage(BaseModel):
    id: int
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str


class ChatMessageResponse(BaseModel):
    message: ChatMessage
    conversation_id: int


class Conversation(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    message_count: int


class ConversationDetails(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    messages: List[ChatMessage]


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """Send a chat message and get AI response."""
    global next_conversation_id, next_message_id
    
    # Get or create conversation
    conversation_id = request.conversation_id
    if conversation_id is None or conversation_id not in conversations_db:
        conversation_id = next_conversation_id
        next_conversation_id += 1
        conversations_db[conversation_id] = {
            "id": conversation_id,
            "title": request.message[:50] + "..." if len(request.message) > 50 else request.message,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "messages": []
        }
    
    # Add user message
    user_message = {
        "id": next_message_id,
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    }
    next_message_id += 1
    conversations_db[conversation_id]["messages"].append(user_message)
    
    # Generate AI response (stub implementation)
    # TODO: Integrate with actual AI/LLM service
    ai_response_content = generate_ai_response(request.message)
    
    ai_message = {
        "id": next_message_id,
        "role": "assistant",
        "content": ai_response_content,
        "timestamp": datetime.utcnow().isoformat()
    }
    next_message_id += 1
    conversations_db[conversation_id]["messages"].append(ai_message)
    
    # Update conversation timestamp
    conversations_db[conversation_id]["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "message": ai_message,
        "conversation_id": conversation_id
    }


@router.get("/history", response_model=List[Conversation])
async def get_conversations():
    """Get list of all conversations."""
    conversations = []
    for conv_id, conv in conversations_db.items():
        conversations.append({
            "id": conv["id"],
            "title": conv["title"],
            "created_at": conv["created_at"],
            "updated_at": conv["updated_at"],
            "message_count": len(conv["messages"])
        })
    
    # Sort by updated_at descending
    conversations.sort(key=lambda x: x["updated_at"], reverse=True)
    return conversations


@router.get("/history/{conversation_id}", response_model=ConversationDetails)
async def get_conversation(conversation_id: int):
    """Get a specific conversation with all messages."""
    if conversation_id not in conversations_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conv = conversations_db[conversation_id]
    return {
        "id": conv["id"],
        "title": conv["title"],
        "created_at": conv["created_at"],
        "updated_at": conv["updated_at"],
        "messages": conv["messages"]
    }


@router.delete("/history/{conversation_id}")
async def delete_conversation(conversation_id: int):
    """Delete a conversation."""
    if conversation_id not in conversations_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    del conversations_db[conversation_id]
    return {"message": "Conversation deleted successfully"}


def generate_ai_response(user_message: str) -> str:
    """
    Generate AI response based on user message.
    
    This is a stub implementation. In production, this should:
    1. Call an LLM API (OpenAI, Claude, etc.)
    2. Use medical knowledge base for context
    3. Apply medical safety filters
    4. Include citations and references
    """
    # Simple rule-based responses for demonstration
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["symptom", "pain", "fever", "cough"]):
        return (
            "I understand you're experiencing symptoms. As an AI medical assistant, "
            "I can provide general information, but I recommend consulting with a healthcare "
            "professional for proper diagnosis and treatment. Can you describe your symptoms "
            "in more detail, including when they started and their severity?"
        )
    elif any(word in message_lower for word in ["medication", "drug", "medicine"]):
        return (
            "I can help provide information about medications. However, please note that "
            "I cannot prescribe medications or replace professional medical advice. "
            "What specific medication information are you looking for?"
        )
    elif any(word in message_lower for word in ["hello", "hi", "hey"]):
        return (
            "Hello! I'm your AI Medical Assistant. I'm here to help with medical information, "
            "symptom assessment, and general health questions. How can I assist you today?"
        )
    elif any(word in message_lower for word in ["thank", "thanks"]):
        return (
            "You're welcome! If you have any more questions about your health or medical "
            "information, feel free to ask. Remember to consult with healthcare professionals "
            "for personalized medical advice."
        )
    else:
        return (
            f"I've noted your question: '{user_message}'. As an AI medical assistant, "
            "I can provide general medical information. However, for personalized medical "
            "advice and treatment, please consult with a qualified healthcare provider. "
            "Is there something specific you'd like to know more about?"
        )
