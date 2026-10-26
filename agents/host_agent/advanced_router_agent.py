"""
BONUS Part A: Advanced Router Agent with Dynamic Routing (+15 points)

This is an OPTIONAL bonus implementation that adds intelligent routing:
  - Analyzes query intent to determine which agents to invoke
  - Uses before_agent_callback to conditionally skip agents
  - Includes a router LLM agent for task decomposition

Architecture:
  Orchestrator (SequentialAgent)
    -> Router Agent (LLM Agent) -- analyzes query, sets routing decision
    -> Sequential Executor (SequentialAgent)
         -> RemoteA2aAgent("customer_data") with before_agent_callback
         -> RemoteA2aAgent("support_specialist") with before_agent_callback

Requirements for bonus points:
  - analyze_query_intent function works correctly (5 pts)
  - Callback functions properly skip/run agents (4 pts)
  - Router agent with dynamic instruction (3 pts)
  - Full orchestrator assembled correctly (3 pts)
"""

import sys
import os
import logging
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Apply A2A compatibility patch BEFORE importing RemoteA2aAgent
from shared import a2a_compat  # noqa: F401

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    GEMINI_MODEL,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [ROUTER_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# =============================================================================
# TODO BONUS: Routing Logic Functions
# =============================================================================
def analyze_query_intent(query: str) -> dict:
  """Determine which agents are needed for a query."""

  query = (query or "").lower()

  data_keywords = [
      "customer", "ticket", "account details",
      "customer id", "ticket id", "list customers",
      "search customer", "lookup", "retrieve",
      "status", "order history",
  ]

  support_keywords = [
      "help", "issue", "problem", "reset",
      "fix", "troubleshoot", "password",
      "login", "billing", "payment",
      "error", "slow", "not working",
      "how do i", "resolve",
  ]

  high_urgency_keywords = [
      "urgent", "immediately", "asap",
      "critical", "emergency",
  ]

  medium_urgency_keywords = [
      "soon", "priority", "important",
  ]

  needs_data = any(word in query for word in data_keywords)
  needs_support = any(word in query for word in support_keywords)

  # Ensure at least one agent executes.
  if not needs_data and not needs_support:
      needs_support = True

  if any(word in query for word in high_urgency_keywords):
      urgency = "high"
  elif any(word in query for word in medium_urgency_keywords):
      urgency = "medium"
  else:
      urgency = "low"

  if needs_data and needs_support:
      execution_mode = "sequential"
  elif needs_data:
      execution_mode = "data_only"
  else:
      execution_mode = "support_only"

  return {
      "needs_data": needs_data,
      "needs_support": needs_support,
      "urgency": urgency,
      "execution_mode": execution_mode,
  }

# =============================================================================
# TODO BONUS: Callback Functions for Dynamic Routing
# =============================================================================

def should_run_customer_data_agent(
    callback_context: CallbackContext
) -> Optional[types.Content]:

    decision = callback_context.state.get(
        "routing_decision", {}
    )

    if not decision.get("needs_data", True):
        logger.info(
            "Skipping Customer Data Agent: not required"
        )
        return types.Content(
            role="model",
            parts=[
                types.Part(
                    text="Customer Data Agent skipped: "
                         "customer data not required."
                )
            ],
        )

    logger.info("Executing Customer Data Agent")
    return None


def should_run_support_agent(
    callback_context: CallbackContext
) -> Optional[types.Content]:

    decision = callback_context.state.get(
        "routing_decision", {}
    )

    if not decision.get("needs_support", True):
        logger.info(
            "Skipping Support Agent: not required"
        )
        return types.Content(
            role="model",
            parts=[
                types.Part(
                    text="Support Agent skipped: "
                         "support assistance not required."
                )
            ],
        )

    logger.info("Executing Support Agent")
    return None





# =============================================================================
# TODO BONUS: Router Agent with Dynamic Instruction
# =============================================================================

def _get_user_query(context) -> str:
    """Extract the user query from ADK context."""

    content = getattr(context, "user_content", None)

    if content and content.parts:
        return " ".join(
            part.text
            for part in content.parts
            if getattr(part, "text", None)
        )

    return ""


def router_before_agent_callback(
    callback_context: CallbackContext
) -> Optional[types.Content]:

    query = _get_user_query(callback_context)

    decision = analyze_query_intent(query)

    callback_context.state["routing_decision"] = decision

    logger.info("Query: %s", query)
    logger.info("Routing decision: %s", decision)

    return None


def create_router_instruction(readonly_context) -> str:
    """Provide a dynamic instruction based on routing state."""

    decision = readonly_context.state.get("routing_decision")

    if not decision:
        query = _get_user_query(readonly_context)
        decision = analyze_query_intent(query)

    return f"""
    You are the Customer Support Query Router.

    Your job is to analyze the user's request and explain
    which specialized agents are required.

    Routing decision:
    - Needs Customer Data Agent: {decision['needs_data']}
    - Needs Support Agent: {decision['needs_support']}
    - Urgency: {decision['urgency']}
    - Execution mode: {decision['execution_mode']}

    Routing rules:
    1. For customer or ticket information, use Customer Data Agent.
    2. For troubleshooting and support, use Support Agent.
    3. For combined requests, use both agents sequentially.
    4. Do not perform customer lookup or troubleshooting yourself.
    5. Do not invent customer details or ticket information.
    6. Keep the routing explanation brief.

    The orchestration callbacks will enforce the routing decision.
    """


# =============================================================================
# TODO BONUS: Create Advanced Agent
# =============================================================================

def create_agent() -> SequentialAgent:
    """Create the advanced dynamically routed A2A orchestrator."""

    router_agent = Agent(
        name="query_router",
        model=GEMINI_MODEL,
        description="Analyzes user intent and determines routing.",
        instruction=create_router_instruction,
        before_agent_callback=router_before_agent_callback,
    )

    remote_customer_data = RemoteA2aAgent(
        name="remote_customer_data",
        description="Retrieves customer profiles and tickets.",
        agent_card=(
            f"{CUSTOMER_DATA_AGENT_URL.rstrip('/')}/"
            f"{AGENT_CARD_WELL_KNOWN_PATH.lstrip('/')}"
        ),
        before_agent_callback=should_run_customer_data_agent,
    )

    remote_support = RemoteA2aAgent(
        name="remote_support_specialist",
        description="Provides support and troubleshooting.",
        agent_card=(
            f"{SUPPORT_AGENT_URL.rstrip('/')}/"
            f"{AGENT_CARD_WELL_KNOWN_PATH.lstrip('/')}"
        ),
        before_agent_callback=should_run_support_agent,
    )

    sequential_executor = SequentialAgent(
        name="conditional_agent_executor",
        description="Runs only the required remote agents.",
        sub_agents=[
            remote_customer_data,
            remote_support,
        ],
    )

    orchestrator = SequentialAgent(
        name="advanced_host_orchestrator",
        description="Dynamically routes customer support queries.",
        sub_agents=[
            router_agent,
            sequential_executor,
        ],
    )

    return orchestrator


