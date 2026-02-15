"""
FastAPI Backend for Glory's Portfolio Chatbot
Provides REST API endpoints for the web interface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
from portfolio_bot import PortfolioChatBot
from datetime import datetime

app = FastAPI(
    title="Glory's Portfolio Chatbot API",
    description="AI-powered chatbot API for Glory's portfolio",
    version="1.0.0"
)

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store chat sessions
chat_sessions: Dict[str, PortfolioChatBot] = {}

# API Configuration
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1"
ABOUT_ME_FOLDER = "./about_me"


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str


def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, PortfolioChatBot]:
    """Get existing session or create new one"""
    if session_id and session_id in chat_sessions:
        return session_id, chat_sessions[session_id]
    
    # Create new session
    new_session_id = f"session_{datetime.now().timestamp()}_{len(chat_sessions)}"
    bot = PortfolioChatBot(
        api_key=API_KEY,
        base_url=BASE_URL,
        about_me_folder=ABOUT_ME_FOLDER
    )
    chat_sessions[new_session_id] = bot
    
    return new_session_id, bot


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Glory's Portfolio Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "POST /chat": "Send a message and get a response",
            "POST /reset": "Reset a chat session",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(chat_sessions),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    Send a message and receive a response from Glory's AI assistant
    """
    try:
        # Get or create session
        session_id, bot = get_or_create_session(request.session_id)
        
        # Get response from bot
        response = bot.chat(request.message)
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_session(session_id: str):
    """Reset a chat session"""
    if session_id in chat_sessions:
        chat_sessions[session_id].reset_conversation()
        return {
            "status": "success",
            "message": f"Session {session_id} has been reset"
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.post("/refresh_knowledge")
async def refresh_knowledge():
    """Refresh knowledge base for all sessions"""
    try:
        # Refresh knowledge for all active sessions
        for bot in chat_sessions.values():
            bot.refresh_knowledge()
        
        return {
            "status": "success",
            "message": "Knowledge base refreshed for all sessions"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def get_sessions():
    """Get list of active sessions"""
    return {
        "active_sessions": len(chat_sessions),
        "session_ids": list(chat_sessions.keys())
    }


if __name__ == "__main__":
    print("🚀 Starting Glory's Portfolio Chatbot API Server...")
    print("📚 Make sure to add documents to the 'about_me' folder!")
    print("🌐 API will be available at: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
