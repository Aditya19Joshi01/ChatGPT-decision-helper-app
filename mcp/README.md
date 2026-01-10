# Decision Helper - MCP Server

This directory contains the MCP (Model Context Protocol) server implementation for the Decision Helper app.

## Responsibilities
The MCP server is a lightweight service that exists to:
1.  Define tools.
2.  Structure data.
3.  Return UI descriptions.

It **does not** make decisions, score options, or run algorithms. All reasoning is handled by the LLM.

## Exposed Tools

### 1. `start_decision`
*   **Purpose**: Normalize and store basic decision inputs.
*   **Input**: Decision title, Option A, Option B.
*   **Output**: Structured decision object.

### 2. `set_priorities`
*   **Purpose**: Capture what matters most to the user.
*   **Input**: List of priorities (max 3).
*   **Output**: Structured priority list.

### 3. `summarize_decision`
*   **Purpose**: Package all collected data into a structured response for UI rendering.
*   **Input**: Decision, options, priorities.
*   **Output**: Comparison data and UI schema (cards, text blocks, buttons).

## UI Rendering
The application does not render HTML on the frontend. Instead, this MCP server returns a **structured UI description**, which ChatGPT renders natively.

**UI Elements Used:**
*   Cards
*   Headings
*   Bullet lists
*   Buttons

## Hosted Instance
This MCP is hosted at:
`https://indirect-ivory-bedbug.fastmcp.app/mcp`
