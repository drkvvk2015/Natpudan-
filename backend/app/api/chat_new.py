"""Chat API endpoints with database and OpenAI integration."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

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

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: str


class ChatMessageResponse(BaseModel):
    message: str
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
        
        # Generate AI response with OpenAI
        ai_response = await generate_ai_response(
            messages=conversation_history,
            system_prompt="You are a helpful medical AI assistant for healthcare professionals. Provide accurate, professional medical information and assistance. Always emphasize when clinical judgment is required and when emergency care should be sought.",
        )
        
        # Save AI response
        create_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
        )
        
        return ChatMessageResponse(
            message=ai_response,
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
