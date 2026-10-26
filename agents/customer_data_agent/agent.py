"""
Part 1: Customer Data Agent (10 points)

Create an ADK Agent that manages customer and ticket data via McpToolset.

This agent should:
  - Use the Gemini model from agents_config
  - Have a descriptive instruction telling the LLM its role and capabilities
  - Include the customer data McpToolset so it can access customer/ticket data

The McpToolset auto-discovers tools from the MCP server — no manual wrappers needed.
You configure which tools the agent can access via the tool_filter in the toolset.

Requirements (README.md Part 1 also grades this agent's McpToolset integration,
error handling and instruction quality; see its Evaluation Rubric for the points):
  - create_agent() returns a configured google.adk.agents.Agent
  - Agent has a detailed instruction string
  - Agent uses create_customer_data_toolset()

Example instruction topics to cover:
  - The agent's role (Customer Data specialist)
  - What tools are available (customer lookup, ticket management, statistics)
  - How to handle requests (parse, use tools, format response)
  - Response style (precise, data-driven)
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from shared.agents_config import GEMINI_MODEL
from shared.mcp_toolset import create_customer_data_toolset
from google.genai import types

# Configure logging for this agent
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [CUSTOMER_DATA_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)



def create_agent() -> Agent:
    """
    Create the Customer Data Agent.

    TODO: Create and return an Agent instance with:
      1. model=GEMINI_MODEL
      2. name='customer_data_agent'
      3. instruction=<your detailed instruction string>
      4. tools=[create_customer_data_toolset()]

    The McpToolset automatically discovers all filtered tools from the MCP
    server. You pass the toolset instance in the tools list — ADK handles
    the rest.

    Example:
        return Agent(
            model=GEMINI_MODEL,
            name='customer_data_agent',
            instruction=\"\"\"
            You are the Customer Data Agent...
            Your capabilities:
            - Retrieve customer information by ID
            - List customers with filters
            ...
            \"\"\",
            tools=[create_customer_data_toolset()],
        )

    Returns:
        Configured Agent instance
    """
    return Agent(
    name="customer_data_agent",

    model=GEMINI_MODEL,

    description=(
        "Manages customer profiles and support tickets "
        "using tools automatically discovered from the MCP server."
    ),

    
    instruction = """
    You are a Customer Data Management Agent responsible for
    managing customer information and support tickets.

    Use the automatically discovered MCP tools to:
    1. Search and retrieve customer information.
    2. Retrieve customer support tickets.
    3. Create and update tickets when requested.
    4. Check ticket status, priority, and assignment.
    5. Summarize customer and ticket information accurately.

    MCP TOOL USAGE:
    - Use the available MCP tools for all customer and ticket operations.
    - Select tools based on their descriptions and input schemas.
    - Provide all required parameters when calling tools.
    - Never fabricate customer records, ticket details, or results.
    - Only use tools that are actually available.

    ERROR HANDLING:
    - If an MCP tool returns an error, explain the problem clearly
      in simple, user-friendly language.
    - Never expose raw stack traces, credentials, or internal
      server details to the user.
    - If a customer or ticket is not found, inform the user
      and suggest checking the identifier.
    - If required parameters are missing, ask the user for
      the missing information before calling the tool.
    - If the MCP server is unavailable, explain that customer
      or ticket information cannot currently be retrieved.
    - If a tool call fails, do not claim the operation succeeded.
    - Retry only when appropriate and safe.
    - Never automatically retry non-idempotent operations such
      as ticket creation without checking whether they succeeded.
    - If an operation partially succeeds, clearly explain what
      completed and what remains unresolved.
    - Offer an actionable next step whenever possible.

    RESPONSE GUIDELINES:
    - Be professional, concise, and helpful.
    - Summarize successful operations clearly.
    - Distinguish verified information from unavailable information.
    - Confirm destructive operations before executing them.
    """,

    tools=[create_customer_data_toolset()]
    
  )
    
