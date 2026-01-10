# Minimal ChatGPT App (Developer Mode) — Decision Helper

## 1. High-level Goal
The goal of this project is not to build a sophisticated product or decision engine. The goal is to:
*   **Learn** how ChatGPT apps work in developer mode.
*   **Understand** how MCP servers, tools, and UI rendering fit together.
*   **Build** a small but complete ChatGPT app that demonstrates:
    *   Tool invocation
    *   Structured inputs/outputs
    *   UI rendered inside ChatGPT
    *   A simple, stateful interaction flow

## 2. Core Idea
**The app is a Two-Option Decision Helper.**

It helps a user think clearly about any decision involving two choices by forcing structure and surfacing trade-offs. Examples:
*   "Should I move to London or Berlin?"
*   "Should I take Job A or Job B?"

The app does not predict outcomes. It simply structures the decision, captures priorities, and presents a clear comparison.

## 3. Design Philosophy
1.  **Simplicity over intelligence**: The backend does not attempt to be smart; ChatGPT handles the reasoning.
2.  **Constraints create value**: Limits options to exactly 2 and priorities to max 3 to prevent overthinking.
3.  **Integration over polish**: The success criterion is demonstrating *how* to build a ChatGPT app, not building the perfect product.

## 4. User Experience (End-to-End Flow)
The app consists of two screens rendered inside ChatGPT:

### Step 1: Input
A structured form asking for:
*   Decision title
*   Option A & Option B
*   Priorities (Cost, Career growth, Lifestyle, etc.)

### Step 2: Result
*   Side-by-side comparison of options.
*   Short explanation of trade-offs.
*   "What this means for you" conclusion.
*   Button to start another decision.

## 5. Technical Scope
*   **No external APIs**
*   **No databases** (in-memory state only)
*   **No authentication**
*   **Hosted MCP**: [https://indirect-ivory-bedbug.fastmcp.app/mcp](https://indirect-ivory-bedbug.fastmcp.app/mcp)

## 6. Project Value
This project demonstrates:
*   Understanding of ChatGPT app architecture.
*   Practical use of MCP tools.
*   Designing tool schemas for LLMs.
*   UI-as-data concepts.

## 7. Framing
"I built a minimal ChatGPT app in developer mode to understand how tools, MCP servers, and UI rendering work together. I intentionally chose a simple decision-making use case so I could focus on integration rather than domain complexity."
