"""Chat API endpoints for AI Medical Assistant conversations."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.api.auth_new import get_current_user
from app.crud import (
    create_conversation,
    get_user_conversations,
    get_conversation,
    delete_conversation as delete_conversation_db,
    create_message,
    get_conversation_messages,
)

router = APIRouter(prefix="/chat", tags=["chat"])


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
async def send_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a chat message and get AI response."""
    # Get or create conversation
    conversation_id = request.conversation_id
    conversation = None
    if conversation_id is not None:
        conversation = get_conversation(db, conversation_id, current_user.id)

    if conversation is None:
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        conversation = create_conversation(db, user_id=current_user.id, title=title)

    create_message(db, conversation.id, "user", request.message)

    # Generate deterministic fallback response for local/test environments.
    ai_response_content = generate_ai_response(request.message)

    ai_message = create_message(db, conversation.id, "assistant", ai_response_content)

    return {
        "message": {
            "id": ai_message.id,
            "role": ai_message.role,
            "content": ai_message.content,
            "timestamp": ai_message.created_at.isoformat(),
        },
        "conversation_id": conversation.id,
    }


@router.get("/history", response_model=List[Conversation])
async def get_conversations_with_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversations = [
        {
            "id": conv.id,
            "title": conv.title or "Untitled conversation",
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "message_count": len(conv.messages),
        }
        for conv in get_user_conversations(db, current_user.id)
    ]
    return conversations


@router.get("/history/{conversation_id}", response_model=ConversationDetails)
async def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific conversation with all messages."""
    conversation = get_conversation(db, conversation_id, current_user.id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages = get_conversation_messages(db, conversation.id)
    return {
        "id": conversation.id,
        "title": conversation.title or "Untitled conversation",
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
            }
            for message in messages
        ],
    }


@router.delete("/history/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a conversation."""
    deleted = delete_conversation_db(db, conversation_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

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
