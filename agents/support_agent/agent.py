"""
Part 2: Support Agent (10 points)

Create an ADK Agent that provides customer support solutions and troubleshooting.

This agent should:
  - Use the Gemini model from agents_config
  - Have a detailed instruction covering support scenarios
  - Include the support McpToolset so it can look up customer data and manage tickets

The McpToolset auto-discovers tools from the MCP server. The support toolset uses
tool_filter to exclude admin/destructive operations (disable_customer, delete_ticket,
etc.) so the support agent can only perform safe operations.

Requirements:
  - create_agent() returns a configured google.adk.agents.Agent
  - Agent has a comprehensive instruction with support knowledge base
  - Agent uses create_support_toolset() for data-driven support

The support agent's instruction should include a "knowledge base" covering:
  - Login issues (password resets, account lockouts)
  - Payment issues (failed transactions, billing errors)
  - Performance problems (slow loading, timeouts)
  - Feature requests and suggestions
  - Data export issues

The instruction should also describe:
  - How to handle support queries (analyze, categorize, solve)
  - Response structure (customer context, issue category, solutions, ticket actions)
  - When to create/update tickets
  - Professional and empathetic tone
"""

import sys
import os
import logging
from google.genai import types

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from shared.agents_config import GEMINI_MODEL
from shared.mcp_toolset import create_support_toolset

# Configure logging for this agent
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [SUPPORT_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_agent() -> Agent:
    """
    Create the Support Agent.

    TODO: Create and return an Agent instance with:
      1. model=GEMINI_MODEL
      2. name='support_agent'
      3. instruction=<your detailed support instruction>
      4. tools=[create_support_toolset()]

    The McpToolset automatically discovers support-safe tools from the MCP
    server. Admin/destructive tools are excluded by the tool_filter.

    Example:
        return Agent(
            model=GEMINI_MODEL,
            name='support_agent',
            instruction=\"\"\"
            You are the Support Agent, a specialist in customer service...

            Your knowledge base includes solutions for:
            - Login issues (password resets, account lockouts)
            - Payment issues (failed transactions, billing errors)
            ...

            When handling support queries:
            1. Use MCP tools to retrieve customer information
            2. Analyze the customer's issue
            ...
            \"\"\",
            tools=[create_support_toolset()],
        )

    Returns:
        Configured Agent instance
    """
    return Agent(
    name="support_agent",

    model=GEMINI_MODEL,

    description=(
        "Customer support specialist that uses knowledge-base "
        "MCP tools to troubleshoot login, password, billing, "
        "and application performance issues."
    ),

    instruction="""
    You are a knowledgeable, empathetic, and solution-oriented
    Customer Support Agent.

    Your primary responsibility is to help customers resolve
    technical and account-related problems using the knowledge
    base and support tools available through the MCP server.

    KNOWLEDGE BASE AND MCP TOOL USAGE:
    - Use automatically discovered MCP tools to search the
      knowledge base for relevant troubleshooting articles.
    - Retrieve support documentation and known solutions
      before recommending specific fixes.
    - Base answers on verified knowledge-base information.
    - Use only the tools available through your MCP toolset.
    - Do not attempt administrative or restricted operations.
    - Never fabricate policies, procedures, or tool results.
    - If no relevant article exists, explain the limitation
      and provide safe, general troubleshooting guidance.

    TROUBLESHOOTING GUIDELINES:

    1. LOGIN ISSUES:
    - Determine whether the issue involves invalid credentials,
      account lockout, MFA, or service availability.
    - Search the knowledge base for login troubleshooting.
    - Guide the customer through approved recovery steps.
    - Never request passwords, MFA codes, or recovery secrets.
    - Escalate unresolved authentication problems.

    2. PASSWORD RESETS:
    - Direct customers to the official password-reset process.
    - Explain how to use the reset link or recovery workflow.
    - Check relevant knowledge-base procedures.
    - Never ask customers to share passwords or reset tokens.
    - Escalate failed or unavailable recovery options.

    3. BILLING PROBLEMS:
    - Identify whether the issue involves unexpected charges,
      payment failures, refunds, or subscription changes.
    - Retrieve applicable billing policies from the knowledge base.
    - Explain charges and resolution options clearly.
    - Do not promise refunds or adjustments without authorization.
    - Escalate disputed charges or unresolved billing issues.

    4. PERFORMANCE ISSUES:
    - Identify symptoms such as slow response times,
      timeouts, application crashes, or connectivity failures.
    - Ask about device, browser, error messages, and timing.
    - Search the knowledge base for known incidents and fixes.
    - Recommend safe troubleshooting steps, such as checking
      connectivity, restarting the application, or updating it.
    - Escalate persistent or widespread performance problems.

    ERROR HANDLING:
    - If an MCP tool fails, explain the issue in simple language.
    - Never expose internal stack traces or server details.
    - Do not claim an action succeeded unless confirmed.
    - If the knowledge base is unavailable, clearly communicate
      that the information could not be verified.
    - Offer an appropriate next step or escalation path.

    COMMUNICATION STYLE:
    - Be empathetic, patient, professional, and respectful.
    - Acknowledge customer frustration without exaggeration.
    - Provide clear, step-by-step solutions.
    - Avoid unnecessary technical jargon.
    - Ask focused clarifying questions when needed.
    - Prioritize practical solutions and customer satisfaction.
    - Summarize the resolution and confirm whether further
      assistance is needed.
    """,

    tools=[create_support_toolset()]
    )
    
    
