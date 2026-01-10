"""
Decision Helper - Minimal ChatGPT App with MCP
================================================
This MCP server helps users decide between two options by:
1. Capturing the decision and options
2. Recording what matters most (priorities)
3. Presenting a structured comparison

Author: Learning MCP
Purpose: Understand ChatGPT app mechanics
"""

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime

# ============================================================================
# 1. INITIALIZE FastMCP SERVER
# ============================================================================

mcp = FastMCP(
    name="Decision Helper",
)

# ============================================================================
# 2. IN-MEMORY STATE (Simple storage for active decisions)
# ============================================================================

# This stores all decisions during the session
# Key: decision_id, Value: decision data
decisions: Dict[str, dict] = {}

# Track the current active decision (for conversational flow)
current_decision_id: Optional[str] = None

# ============================================================================
# 3. PYDANTIC MODELS (Type-safe data structures)
# ============================================================================

class DecisionResponse(BaseModel):
    """Response when starting a new decision"""
    decision_id: str
    title: str
    option_a: str
    option_b: str
    status: str = "created"
    message: str


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
    fit_score: str  # e.g., "Strong fit for Cost priority"


class SummaryResponse(BaseModel):
    """Final decision summary with structured UI data"""
    decision_id: str
    title: str
    option_a_card: ComparisonCard
    option_b_card: ComparisonCard
    trade_offs: str
    what_this_means: str
    status: str = "completed"


# ============================================================================
# 4. TOOL 1: start_decision
# ============================================================================

@mcp.tool()
def start_decision(
    title: str,
    option_a: str,
    option_b: str
) -> DecisionResponse:
    """
    Start a new decision comparison between two options.
    
    Use this tool when a user wants to compare two choices or make a decision.
    This captures the basic decision framework.
    
    Args:
        title: The decision question (e.g., "Should I move to London or Berlin?")
        option_a: First option to consider (e.g., "London")
        option_b: Second option to consider (e.g., "Berlin")
    
    Returns:
        A new decision object with a unique ID
    
    Example:
        User: "Help me decide between taking Job A or Job B"
        Call: start_decision(
            title="Job Decision",
            option_a="Job A - Tech Startup",
            option_b="Job B - Big Corp"
        )
    """
    global current_decision_id
    
    # Generate unique ID for this decision
    decision_id = str(uuid.uuid4())[:8]  # Short ID for readability
    
    # Store decision data
    decisions[decision_id] = {
        "title": title,
        "option_a": option_a,
        "option_b": option_b,
        "priorities": [],
        "created_at": datetime.now().isoformat()
    }
    
    # Set as current active decision
    current_decision_id = decision_id
    
    return DecisionResponse(
        decision_id=decision_id,
        title=title,
        option_a=option_a,
        option_b=option_b,
        message=f"Decision '{title}' created! Next, I'll ask about your priorities."
    )


# ============================================================================
# 5. TOOL 2: set_priorities
# ============================================================================

@mcp.tool()
def set_priorities(
    priorities: List[str],
    decision_id: Optional[str] = None
) -> PrioritiesResponse:
    """
    Set what matters most for this decision (max 3 priorities).
    
    Valid priorities are:
    - Cost
    - Career growth
    - Lifestyle
    - Work-life balance
    - Stability
    - Flexibility
    
    Args:
        priorities: List of 1-3 priorities that matter most
        decision_id: Optional. If not provided, uses current active decision
    
    Returns:
        Updated decision with priorities set
    
    Example:
        User: "I care most about cost and lifestyle"
        Call: set_priorities(priorities=["Cost", "Lifestyle"])
    """
    global current_decision_id
    
    # Use provided ID or fall back to current decision
    target_id = decision_id or current_decision_id
    
    if not target_id or target_id not in decisions:
        raise ValueError("No active decision found. Please start a decision first.")
    
    # Validate max 3 priorities
    if len(priorities) > 3:
        raise ValueError("Please select maximum 3 priorities")
    
    # Valid priority options
    valid_priorities = {
        "Cost", "Career growth", "Lifestyle", 
        "Work-life balance", "Stability", "Flexibility"
    }
    
    # Normalize and validate
    normalized = []
    for p in priorities:
        # Case-insensitive matching
        matched = next((v for v in valid_priorities if v.lower() == p.lower()), None)
        if matched:
            normalized.append(matched)
        else:
            # Accept it anyway but flag it
            normalized.append(p)
    
    # Update decision
    decisions[target_id]["priorities"] = normalized
    
    return PrioritiesResponse(
        decision_id=target_id,
        priorities=normalized,
        message=f"Got it! Your priorities are: {', '.join(normalized)}"
    )


# ============================================================================
# 6. TOOL 3: summarize_decision
# ============================================================================

@mcp.tool()
def summarize_decision(
    decision_id: Optional[str] = None
) -> SummaryResponse:
    """
    Generate a structured comparison summary with trade-off analysis.
    
    This tool packages all collected data into a clear side-by-side comparison
    that ChatGPT can render as cards and formatted text.
    
    Args:
        decision_id: Optional. If not provided, uses current active decision
    
    Returns:
        Structured comparison data with:
        - Side-by-side option cards
        - Trade-off analysis
        - Personalized conclusion
    
    Example:
        After user has set priorities, call this to generate final summary.
    """
    global current_decision_id
    
    # Use provided ID or fall back to current decision
    target_id = decision_id or current_decision_id
    
    if not target_id or target_id not in decisions:
        raise ValueError("No active decision found.")
    
    decision = decisions[target_id]
    
    # Extract data
    title = decision["title"]
    option_a = decision["option_a"]
    option_b = decision["option_b"]
    priorities = decision.get("priorities", [])
    
    # Build comparison cards (structured data, not logic)
    # ChatGPT will use this structure to generate the actual reasoning
    
    option_a_card = ComparisonCard(
        option_name=option_a,
        strengths=[
            f"Data point for {option_a} (ChatGPT will fill this based on context)",
            "Placeholder strength 2",
            "Placeholder strength 3"
        ],
        considerations=[
            "Consideration 1 for context",
            "Consideration 2 for context"
        ],
        fit_score=f"Alignment with priorities: {', '.join(priorities[:2]) if priorities else 'general'}"
    )
    
    option_b_card = ComparisonCard(
        option_name=option_b,
        strengths=[
            f"Data point for {option_b} (ChatGPT will fill this based on context)",
            "Placeholder strength 2",
            "Placeholder strength 3"
        ],
        considerations=[
            "Consideration 1 for context",
            "Consideration 2 for context"
        ],
        fit_score=f"Alignment with priorities: {', '.join(priorities[:2]) if priorities else 'general'}"
    )
    
    # Trade-off template (ChatGPT fills in the reasoning)
    trade_offs = f"""
    This decision involves trade-offs between {option_a} and {option_b}.
    Based on your priorities ({', '.join(priorities) if priorities else 'general factors'}),
    here are the key considerations...
    """
    
    # Conclusion template
    what_this_means = f"""
    Given what matters most to you, here's what to consider:
    [ChatGPT will provide personalized guidance based on the conversation context]
    """
    
    return SummaryResponse(
        decision_id=target_id,
        title=title,
        option_a_card=option_a_card,
        option_b_card=option_b_card,
        trade_offs=trade_offs.strip(),
        what_this_means=what_this_means.strip()
    )


# ============================================================================
# 7. HELPER TOOL: reset_decision (for starting fresh)
# ============================================================================

@mcp.tool()
def reset_decision() -> dict:
    """
    Clear the current decision and start fresh.
    
    Use this when the user wants to analyze a completely new decision.
    
    Returns:
        Confirmation that state has been reset
    """
    global current_decision_id
    current_decision_id = None
    
    return {
        "status": "reset",
        "message": "Ready for a new decision! What would you like to decide?"
    }


# ============================================================================
# 8. HELPER TOOL: get_current_decision (for context)
# ============================================================================

@mcp.tool()
def get_current_decision() -> dict:
    """
    Retrieve the current active decision details.
    
    Useful if ChatGPT needs to reference what's been captured so far.
    
    Returns:
        Current decision data or empty state
    """
    if not current_decision_id or current_decision_id not in decisions:
        return {
            "status": "no_active_decision",
            "message": "No decision in progress"
        }
    
    return {
        "status": "active",
        "decision": decisions[current_decision_id]
    }


# ============================================================================
# 9. RUN SERVER
# ============================================================================

if __name__ == "__main__":
    # FastMCP handles all the MCP protocol details
    # Just run: fastmcp dev main.py
    mcp.run()