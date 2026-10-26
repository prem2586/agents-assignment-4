"""
BONUS Part B: Parallel Router Agent (+10 points)

This is an OPTIONAL bonus implementation that executes agents in parallel.

Architecture:
  Orchestrator (SequentialAgent)
    -> Parallel Worker (ParallelAgent)
         -> RemoteA2aAgent("customer_data") with after_agent_callback -> state
         -> RemoteA2aAgent("support_specialist") with after_agent_callback -> state
    -> Summary Agent (LLM Agent) -- synthesizes parallel results

Key concepts:
  - ParallelAgent runs sub-agents concurrently instead of one after another
  - RemoteA2aAgent has NO output_key field (passing one raises a pydantic
    "Extra inputs are not permitted" ValidationError). Store each remote agent's
    output in state with an after_agent_callback instead.
  - Summary agent reads state and combines outputs into cohesive response

Requirements for bonus points:
  - RemoteA2aAgent output stored in state via after_agent_callback (3 pts)
  - ParallelAgent correctly assembled (2 pts)
  - Summary agent with dynamic instruction reading state (3 pts)
  - Full orchestrator assembled correctly (2 pts)
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Apply A2A compatibility patch
from shared import a2a_compat  # noqa: F401

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    GEMINI_MODEL,
)

logger = logging.getLogger(__name__)

# =============================================================================
# TODO BONUS: Summary Instruction Function
# =============================================================================

def create_summary_instruction(
    readonly_context: ReadonlyContext,
) -> str:
    """
    Read parallel agent outputs from state and create
    instructions for the summary LLM.
    """

    data_output = readonly_context.state.get(
        "customer_data_output",
        "",
    )

    support_output = readonly_context.state.get(
        "support_specialist_output",
        "",
    )

    logger.info(
        "Creating summary: customer=%d chars, support=%d chars",
        len(data_output),
        len(support_output),
    )

    return f"""
    You are the Customer Support Summary Agent.

    Two specialized agents have executed in parallel.

    Your task is to combine their findings into one coherent,
    accurate, business-friendly response.

    CUSTOMER DATA AGENT RESULT:
    {data_output or "No customer data was returned."}

    SUPPORT SPECIALIST AGENT RESULT:
    {support_output or "No support response was returned."}

    INSTRUCTIONS:

    1. Combine relevant information from both agents.
    2. Present customer details clearly when available.
    3. Include support recommendations or resolutions.
    4. Remove duplicated information.
    5. Do not invent customer records, tickets, or actions.
    6. If the agents disagree, explain the discrepancy.
    7. If an agent returned no information, do not assume
      that its task succeeded.
    8. Keep the final response concise and actionable.

    Return a single consolidated response.
    """


# =============================================================================
# TODO BONUS: Create Parallel Agent
# =============================================================================


def create_agent() -> SequentialAgent:
    """
    Create a parallel A2A orchestrator with summary synthesis.
    """

    logger.info("Creating Parallel Router Agent")

    # --------------------------------------------------------
    # Step 1: Customer Data Remote Agent
    # --------------------------------------------------------

    customer_data_card_url = (
        f"{CUSTOMER_DATA_AGENT_URL.rstrip('/')}/"
        f"{AGENT_CARD_WELL_KNOWN_PATH.lstrip('/')}"
    )

    remote_customer_data = RemoteA2aAgent(
        name="remote_customer_data",
        description=(
            "Retrieves customer profiles, account information, "
            "and customer support tickets."
        ),
        agent_card=customer_data_card_url,
        after_agent_callback=customer_data_after_callback,
    )

    # --------------------------------------------------------
    # Step 2: Support Specialist Remote Agent
    # --------------------------------------------------------

    support_card_url = (
        f"{SUPPORT_AGENT_URL.rstrip('/')}/"
        f"{AGENT_CARD_WELL_KNOWN_PATH.lstrip('/')}"
    )

    remote_support = RemoteA2aAgent(
        name="remote_support_specialist",
        description=(
            "Provides customer support, troubleshooting, "
            "and issue resolution recommendations."
        ),
        agent_card=support_card_url,
        after_agent_callback=support_after_callback,
    )

    # --------------------------------------------------------
    # Step 3: Parallel Execution
    # --------------------------------------------------------

    parallel_worker_agent = ParallelAgent(
        name="parallel_support_workers",
        description=(
            "Runs Customer Data and Support Specialist "
            "agents concurrently."
        ),
        sub_agents=[
            remote_customer_data,
            remote_support,
        ],
    )

    # --------------------------------------------------------
    # Step 4: Summary Agent
    # --------------------------------------------------------

    summary_agent = Agent(
        name="parallel_response_summary",
        model=GEMINI_MODEL,
        description=(
            "Synthesizes the outputs of parallel agents "
            "into a unified response."
        ),
        instruction=create_summary_instruction,
        include_contents="none",
    )

    # --------------------------------------------------------
    # Step 5: Sequential Orchestrator
    # --------------------------------------------------------

    orchestrator = SequentialAgent(
        name="parallel_host_orchestrator",
        description=(
            "Executes remote customer support agents in "
            "parallel and synthesizes their responses."
        ),
        sub_agents=[
            parallel_worker_agent,
            summary_agent,
        ],
    )

    logger.info(
        "Parallel Router created successfully"
    )

    return orchestrator


def support_after_callback(
    callback_context: CallbackContext,
):
    """
    Store Support Specialist output in session state.
    """

    return save_agent_output(
        callback_context,
        "support_specialist_output",
    )

def customer_data_after_callback(
    callback_context: CallbackContext,
):
    """
    Store Customer Data Agent output in session state.
    """

    return save_agent_output(
        callback_context,
        "customer_data_output",
    )


def save_agent_output(
    callback_context: CallbackContext,
    state_key: str,
):
    """
    Find the latest response produced by the current remote
    agent and store its text in session state.
    """

    agent_name = callback_context.agent_name

    logger.info(
        "Collecting output from agent: %s",
        agent_name,
    )

    output = ""

    for event in reversed(callback_context.session.events):

        if (
            event.author == agent_name
            and event.content
            and event.content.parts
        ):
            output = "".join(
                part.text or ""
                for part in event.content.parts
            )
            break

    callback_context.state[state_key] = output

    logger.info(
        "Stored output for %s: %d characters",
        state_key,
        len(output),
    )

    if not output:
        logger.warning(
            "No response text found for agent %s",
            agent_name,
        )

    return None

