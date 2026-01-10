"""
Decision Helper - ChatGPT Actions Version
==========================================
This FastAPI server exposes REST endpoints that work as ChatGPT Actions.
Same logic as MCP version, but using OpenAPI/REST protocol.

Author: Learning ChatGPT Actions
Purpose: Understand how ChatGPT Custom GPTs integrate with external APIs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime

# ============================================================================
# 1. INITIALIZE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Decision Helper API",
    description="Help users make decisions between two options by structuring their thinking",
    version="1.0.0",
    servers=[
        {"url": "http://localhost:8000", "description": "Local development"},
        # Add your deployment URL here when you deploy
        # {"url": "https://your-app.railway.app", "description": "Production"}
    ]
)

# Enable CORS for ChatGPT to access your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 2. IN-MEMORY STATE (Simple storage for active decisions)
# ============================================================================

# This stores all decisions during the session
# Key: decision_id, Value: decision data
decisions: Dict[str, dict] = {}

# Track sessions to support multiple users
# In production, you'd use a database
sessions: Dict[str, str] = {}  # session_id -> current_decision_id

# ============================================================================
# 3. PYDANTIC MODELS (Request/Response schemas for OpenAPI)
# ============================================================================

class StartDecisionRequest(BaseModel):
    """Request to start a new decision"""
    title: str = Field(..., description="The decision question", example="Should I move to London or Berlin?")
    option_a: str = Field(..., description="First option to consider", example="London")
    option_b: str = Field(..., description="Second option to consider", example="Berlin")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")

class DecisionResponse(BaseModel):
    """Response when starting a new decision"""
    decision_id: str
    title: str
    option_a: str
    option_b: str
    status: str = "created"
    message: str

class SetPrioritiesRequest(BaseModel):
    """Request to set priorities"""
    priorities: List[str] = Field(
        ..., 
        description="List of 1-3 priorities that matter most",
        example=["Cost", "Lifestyle"],
        max_items=3
    )
    decision_id: Optional[str] = Field(None, description="Decision ID. If not provided, uses current session decision")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")

class PrioritiesResponse(BaseModel):
    """Response when setting priorities"""
    decision_id: str
    priorities: List[str]
    status: str = "priorities_set"
    message: str

class ComparisonCard(BaseModel):
    """Structured comparison for one option"""
    option_name: str
    strengths: List[str]
    considerations: List[str]
    fit_score: str

class SummaryResponse(BaseModel):
    """Final decision summary with structured UI data"""
    decision_id: str
    title: str
    option_a_card: ComparisonCard
    option_b_card: ComparisonCard
    trade_offs: str
    what_this_means: str
    status: str = "completed"

class SummaryRequest(BaseModel):
    """Request to generate summary"""
    decision_id: Optional[str] = Field(None, description="Decision ID to summarize")
    session_id: Optional[str] = Field(None, description="Session ID")

class ResetResponse(BaseModel):
    """Response when resetting"""
    status: str
    message: str

class DecisionStatusResponse(BaseModel):
    """Current decision status"""
    status: str
    decision: Optional[dict] = None
    message: str

# ============================================================================
# 4. HELPER FUNCTIONS
# ============================================================================

def get_current_decision_id(session_id: Optional[str], decision_id: Optional[str]) -> Optional[str]:
    """Get decision ID from session or explicit ID"""
    if decision_id:
        return decision_id
    if session_id and session_id in sessions:
        return sessions[session_id]
    return None

# ============================================================================
# 5. API ENDPOINTS (ChatGPT Actions)
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Decision Helper API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/start-decision", response_model=DecisionResponse)
def start_decision(request: StartDecisionRequest):
    """
    Start a new decision comparison between two options.
    
    This endpoint captures the basic decision framework with two options.
    Use this when a user wants to compare two choices.
    
    Example usage:
    - "Help me decide between Job A and Job B"
    - "Should I move to London or Berlin?"
    - "Which laptop should I buy: MacBook or ThinkPad?"
    """
    # Generate unique IDs
    decision_id = str(uuid.uuid4())[:8]
    session_id = request.session_id or str(uuid.uuid4())[:8]
    
    # Store decision data
    decisions[decision_id] = {
        "title": request.title,
        "option_a": request.option_a,
        "option_b": request.option_b,
        "priorities": [],
        "created_at": datetime.now().isoformat(),
        "session_id": session_id
    }
    
    # Track in session
    sessions[session_id] = decision_id
    
    return DecisionResponse(
        decision_id=decision_id,
        title=request.title,
        option_a=request.option_a,
        option_b=request.option_b,
        message=f"Decision '{request.title}' created! Next, tell me what matters most to you (priorities)."
    )

@app.post("/set-priorities", response_model=PrioritiesResponse)
def set_priorities(request: SetPrioritiesRequest):
    """
    Set what matters most for this decision (max 3 priorities).
    
    Valid priorities include:
    - Cost
    - Career growth
    - Lifestyle
    - Work-life balance
    - Stability
    - Flexibility
    
    You can also use custom priorities based on user input.
    
    Example usage:
    - "I care most about cost and lifestyle"
    - "My priorities are career growth and work-life balance"
    """
    # Get decision ID
    target_id = get_current_decision_id(request.session_id, request.decision_id)
    
    if not target_id or target_id not in decisions:
        raise HTTPException(
            status_code=404,
            detail="No active decision found. Please start a decision first using /start-decision"
        )
    
    # Validate max 3 priorities
    if len(request.priorities) > 3:
        raise HTTPException(
            status_code=400,
            detail="Please select maximum 3 priorities"
        )
    
    # Valid priority options (flexible - accept custom too)
    valid_priorities = {
        "Cost", "Career growth", "Lifestyle", 
        "Work-life balance", "Stability", "Flexibility"
    }
    
    # Normalize priorities
    normalized = []
    for p in request.priorities:
        # Case-insensitive matching
        matched = next((v for v in valid_priorities if v.lower() == p.lower()), None)
        normalized.append(matched if matched else p.title())
    
    # Update decision
    decisions[target_id]["priorities"] = normalized
    
    return PrioritiesResponse(
        decision_id=target_id,
        priorities=normalized,
        message=f"Got it! Your priorities are: {', '.join(normalized)}. Ready to generate comparison!"
    )

@app.post("/summarize", response_model=SummaryResponse)
def summarize_decision(request: SummaryRequest):
    """
    Generate a structured comparison summary with trade-off analysis.
    
    This packages all collected data into a clear side-by-side comparison.
    Call this after the user has set their priorities.
    
    Returns structured data that can be rendered as:
    - Side-by-side comparison cards
    - Trade-off analysis
    - Personalized conclusion
    """
    # Get decision ID
    target_id = get_current_decision_id(request.session_id, request.decision_id)
    
    if not target_id or target_id not in decisions:
        raise HTTPException(
            status_code=404,
            detail="No active decision found."
        )
    
    decision = decisions[target_id]
    
    # Extract data
    title = decision["title"]
    option_a = decision["option_a"]
    option_b = decision["option_b"]
    priorities = decision.get("priorities", [])
    
    # Build comparison cards
    # Note: These are placeholder structures
    # In a real app, you might use AI or data to populate these
    option_a_card = ComparisonCard(
        option_name=option_a,
        strengths=[
            f"Consider the benefits of {option_a}",
            "Evaluate how it aligns with your goals",
            "Think about long-term implications"
        ],
        considerations=[
            "What are the potential drawbacks?",
            "How does this fit your current situation?"
        ],
        fit_score=f"Alignment with your priorities: {', '.join(priorities[:2]) if priorities else 'general evaluation'}"
    )
    
    option_b_card = ComparisonCard(
        option_name=option_b,
        strengths=[
            f"Consider the benefits of {option_b}",
            "Evaluate how it aligns with your goals",
            "Think about long-term implications"
        ],
        considerations=[
            "What are the potential drawbacks?",
            "How does this fit your current situation?"
        ],
        fit_score=f"Alignment with your priorities: {', '.join(priorities[:2]) if priorities else 'general evaluation'}"
    )
    
    # Generate trade-off analysis
    priority_text = ', '.join(priorities) if priorities else 'general factors'
    trade_offs = f"This decision involves weighing {option_a} against {option_b}. Based on your priorities ({priority_text}), consider how each option serves your goals."
    
    what_this_means = f"Given what matters most to you, reflect on which option better aligns with your priorities of {priority_text}. Consider both short-term and long-term implications."
    
    return SummaryResponse(
        decision_id=target_id,
        title=title,
        option_a_card=option_a_card,
        option_b_card=option_b_card,
        trade_offs=trade_offs,
        what_this_means=what_this_means
    )

@app.post("/reset", response_model=ResetResponse)
def reset_decision(session_id: Optional[str] = None):
    """
    Clear the current decision and start fresh.
    
    Use this when the user wants to analyze a completely new decision.
    """
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    return ResetResponse(
        status="reset",
        message="Ready for a new decision! What would you like to decide?"
    )

@app.get("/status", response_model=DecisionStatusResponse)
def get_decision_status(session_id: Optional[str] = None, decision_id: Optional[str] = None):
    """
    Retrieve the current decision details.
    
    Useful for checking what's been captured so far.
    """
    target_id = get_current_decision_id(session_id, decision_id)
    
    if not target_id or target_id not in decisions:
        return DecisionStatusResponse(
            status="no_active_decision",
            message="No decision in progress"
        )
    
    return DecisionStatusResponse(
        status="active",
        decision=decisions[target_id],
        message="Decision found"
    )

# ============================================================================
# 6. RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         Decision Helper API - ChatGPT Actions            ║
    ║                                                          ║
    ║  Server starting on: http://localhost:8000               ║
    ║  API Docs: http://localhost:8000/docs                    ║
    ║  OpenAPI Schema: http://localhost:8000/openapi.json      ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )