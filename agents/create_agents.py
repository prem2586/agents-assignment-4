"""
Part 2: Agent Factory and AgentCard Definitions (Agent Cards, 10 points)

Create AgentCards for A2A discovery and a factory function to create all agents.

AgentCards are the A2A protocol's way of advertising agent capabilities.
They include metadata like name, URL, description, skills, and examples.

Requirements:
  - create_customer_data_agent_card() returns valid AgentCard
  - create_support_agent_card() returns valid AgentCard
  - create_host_agent_card() returns valid AgentCard
  - create_all_agents() returns dict with all agents and cards

Each AgentCard needs:
  - name: Human-readable agent name
  - url: The agent's server URL
  - description: What the agent does
  - version: Version string (e.g., '1.0')
  - capabilities: AgentCapabilities(streaming=True)
  - default_input_modes: ['text/plain']
  - default_output_modes: ['text/plain'] or ['application/json']
  - preferred_transport: TransportProtocol.jsonrpc
  - skills: List of AgentSkill with id, name, description, tags, examples
"""

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    HOST_AGENT_URL,
)

# Import agent creation functions
from customer_data_agent.agent import create_agent as create_customer_data_agent
from support_agent.agent import create_agent as create_support_agent
from host_agent.agent import create_agent as create_host_agent


# =============================================================================
# TODO 1: Customer Data Agent Card
# =============================================================================

def create_customer_data_agent_card() -> AgentCard:
    """
    Create AgentCard for Customer Data Agent.

    """

    return AgentCard(
        name='Manage Customer Data',
        description=(
            "Manages customer records and support tickets "
            "using MCP tools."
        ),
        url=CUSTOMER_DATA_AGENT_URL,
        version='1.0',
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=['text/plain'],
        default_output_modes=['application/json'],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="customer_management",
                name="Customer Management",
                description=(
                    "Searches and retrieves customer profiles "
                    "and account information."
                ),
                tags=["customer", "account", "lookup"],
                examples=[
                    "Find customer CUST-001",
                    "Get account details for customer CUST-002"
                ]
            ),
            AgentSkill(
                id="ticket_management",
                name="Ticket Management",
                description=(
                    "Retrieves, creates, and updates customer "
                    "support tickets."
                ),
                tags=["ticket", "support", "status"],
                examples=[
                    "Show tickets for customer CUST-001",
                    "Check the status of ticket TKT-100"
                ]
            )
        ]


    )
    


# =============================================================================
# TODO 2: Support Agent Card
# =============================================================================

def create_support_agent_card() -> AgentCard:
    """
    Create AgentCard for Support Agent.

    """
    return AgentCard(
        name="Support Agent",
        description=(
            "Provides knowledge-base troubleshooting guidance "
            "for customer support issues."
        ),
        url=SUPPORT_AGENT_URL,
        version="1.0",
        capabilities=AgentCapabilities(
            streaming=False
        ),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="authentication_support",
                name="Login and Password Support",
                description=(
                    "Troubleshoots login failures, account "
                    "access, and password-reset problems."
                ),
                tags=["login", "password", "authentication"],
                examples=[
                    "I cannot log in to my account",
                    "How do I reset my password?"
                ]
            ),
            AgentSkill(
                id="billing_support",
                name="Billing Support",
                description=(
                    "Provides troubleshooting guidance for "
                    "payments, charges, and billing issues."
                ),
                tags=["billing", "payment", "refund"],
                examples=[
                    "Why was I charged twice?",
                    "My payment keeps failing"
                ]
            ),
            AgentSkill(
                id="performance_support",
                name="Performance Troubleshooting",
                description=(
                    "Helps diagnose slow applications, "
                    "timeouts, and performance problems."
                ),
                tags=["performance", "latency", "troubleshooting"],
                examples=[
                    "The application is running slowly",
                    "I keep getting timeout errors"
                ]
            )
        ]
    )


# =============================================================================
# TODO 3: Host Agent Card
# =============================================================================

def create_host_agent_card() -> AgentCard:
    """
    Create AgentCard for Host Agent (Orchestrator).

    """
    return AgentCard(
        name="Customer Support Host Agent",
        description=(
            "Orchestrates customer data lookup and support "
            "troubleshooting through remote A2A agents."
        ),
        url=HOST_AGENT_URL,
        version="1.0",
        capabilities=AgentCapabilities(
            streaming=False
        ),
        default_input_modes=['text/plain'],
        default_output_modes=['text/plain'],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="support_orchestration",
                name="Customer Support Orchestration",
                description=(
                    "Coordinates customer data retrieval "
                    "followed by support troubleshooting."
                ),
                tags=["orchestration", "a2a", "support"],
                examples=[
                    "Find customer CUST-001 and troubleshoot their login issue",
                    "Check ticket TKT-100 and recommend next steps"
                ]
            ),
            AgentSkill(
                id="customer_issue_resolution",
                name="Customer Issue Resolution",
                description=(
                    "Combines customer and ticket context "
                    "with knowledge-base guidance."
                ),
                tags=["customer", "ticket", "resolution"],
                examples=[
                    "Review my billing ticket and suggest a solution",
                    "Look up my account and help resolve a performance issue"
                ]
            )
        ]
    )


# =============================================================================
# TODO 4: Factory Function
# =============================================================================

def create_all_agents():
    
    """
    Create all agents and their A2A agent cards
    for the customer support system.
    """

    return {
        "customer_data": {
            "agent": create_customer_data_agent(),
            "card": create_customer_data_agent_card(),
            "port": 10020,
        },
        "support": {
            "agent": create_support_agent(),
            "card": create_support_agent_card(),
            "port": 10021,
        },
        "host": {
            "agent": create_host_agent(),
            "card": create_host_agent_card(),
            "port": 10022,
        },
    }
    
