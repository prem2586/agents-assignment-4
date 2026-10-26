# Assignment 4: Reflection

Student Name: Prem Kumar

## Part 1: MCP Tools + Customer Data Agent

### Toolset Design Decisions

**Which MCP tools did you include in each tool_filter, and why?**

I configured the Customer Data Agent with the full MCP toolset for customer and ticket operations. The Support Agent uses a filtered toolset that excludes exactly five administrative tools: disable_customer, activate_customer, delete_ticket, add_customer, and update_customer. This division applies the principle of least privilege: the support specialist can investigate and advise without being granted unnecessary record-modification privileges.

**How does the support toolset’s filter limit what the support agent can do?**

The Support Agent cannot invoke the excluded tools to disable or activate accounts, delete tickets, add customers, or update customer records. It can still use permitted tools for lookups and support-related investigation. This is a tool-access restriction, not merely a behavioral instruction.

### Data Agent Instruction

**What capabilities did you include in the system instruction?**

The Customer Data Agent is responsible for retrieving customer profiles, account details, and support-ticket information using MCP tools. Its instruction emphasizes accurate tool-grounded answers, clear reporting, and avoiding invented customer information.

**How does the instruction guide the agent’s tool selection?**

The instruction encourages matching the requested operation to the relevant MCP tool: customer queries use customer lookup capabilities, and ticket questions use ticket retrieval capabilities. It should report missing information instead of fabricating a result.

## Part 2: Multi-Agent A2A System

### Support Agent Design

**What knowledge did you embed in the support agent’s instruction?**

The Support Agent was given troubleshooting guidance for authentication and password resets, billing and payment problems, and application performance issues. It should provide practical next steps, explain uncertainty, and escalate when the available information is insufficient.

**How does it combine its knowledge base with its filtered MCP toolset?**

Its instruction provides general diagnostic knowledge, while permitted MCP lookup tools supply customer-specific facts. It uses the retrieved facts to tailor guidance without acquiring administrative permissions.

### Host Agent Orchestration

**How does the SequentialAgent coordinate between sub-agents?**

The Basic Host uses a Google ADK SequentialAgent with remote Customer Data and Support agents, executed in that order through RemoteA2aAgent. In testing, Basic mode returned responses from both agents, demonstrating sequential orchestration and working A2A communication.

**What happens when the Customer Data Agent returns data to the Support Agent?**

The Customer Data Agent emits a response as an A2A/ADK event, after which the host proceeds to the Support Agent. Earlier context may be available depending on the orchestration flow; explicitly saving structured customer results in shared session state would make data transfer more predictable.

### A2A Protocol Insights

**How does agent discovery work via AgentCards?**

Each remote service publishes an AgentCard with its identity, skills, capabilities, and communication endpoint. The host retrieves the cards to configure remote-agent communication. My Customer Data and Support A2A services ran on ports 10020 and 10021.

**What role does the .well-known/agent-card.json endpoint play?**

It is the standard discovery location, such as http://localhost:10020/.well-known/agent-card.json. Both AgentCard endpoints returned HTTP 200 during testing, confirming that the host could retrieve the remote agents’ metadata.

**How does RemoteA2aAgent differ from direct function calls?**

RemoteA2aAgent sends structured requests to separately running services over A2A/HTTP instead of invoking local Python functions. This enables independent deployment and specialization but adds serialization, network, and failure-handling overhead.

## Part 3: Challenges and Solutions

### Technical Challenges

**What was the most difficult part of the implementation?**

The hardest part was coordinating MCP, Google ADK, and A2A correctly while handling asynchronous APIs and model service limits. I encountered coroutine and toolset validation issues, AgentCard configuration problems, unsupported Agent retry_options parameters, and Gemini 503 availability and 429 daily free-tier quota errors.

**How did you debug agent communication issues?**

I tested services independently, checked the MCP SSE endpoint at http://localhost:8080/sse, verified AgentCard URLs and HTTP 200 responses, and inspected ADK Web and server logs. Routing logs showed a password-reset query classified as support_only and the Customer Data Agent skipped. API error payloads helped distinguish orchestration failures from model quotas.

### Architecture Decisions

**Why is the SequentialAgent pattern appropriate for this use case?**

Customer-specific support can depend on first retrieving account or ticket data. SequentialAgent makes this order explicit, is straightforward to trace, and offers a simple baseline for comparison with dynamic and parallel routing.

**What are the trade-offs vs. direct agent calls?**

The multi-agent approach provides modularity, reuse, independent deployment, and specialist boundaries. It also adds network latency, more LLM calls, context-sharing complexity, and additional failure modes. Direct calls are simpler for tightly coupled or trivial operations.

## Bonus: Routing Modes

### Advanced Router

**How does dynamic routing decide which agents to call?**

A query-intent analyzer sets needs_data, needs_support, urgency, and execution_mode. The execution mode is data_only, support_only, or sequential. For example, a password-reset question was routed to Support only, avoiding an unnecessary Customer Data call.

**What callback patterns did you use?**

A router before_agent_callback writes the routing decision to session state. Conditional before_agent_callback functions on the remote agents inspect that decision and either allow execution or return a skip response. This makes routing visible and avoids unnecessary work.

### Parallel Router

**How does parallel execution improve latency?**

ParallelAgent launches Customer Data and Support concurrently, so independent worker time can approach the slower worker rather than the sum of both. This does not guarantee a faster final response because the additional synthesis stage and network/model overhead still take time.

**What synthesis strategy did you use to combine results?**

after_agent_callback functions capture outputs into customer_data_output and support_specialist_output in session state. A final Summary Agent reads those outputs and produces one consolidated answer, avoiding duplication and unsupported details.

### Mode Comparison

Observed measurements from ADK Web; Basic mode latency was not recorded.

**Basic Router token usage limitation:** The Basic Router successfully returned responses from both agents. However, token usage metadata was not exposed in the Host Agent's ADK Web event view because the underlying LLM calls were executed by remote A2A agents. Therefore, total token consumption could not be reliably measured.

| Mode | Agents Called | Latency | Token Usage |
| --- | --- | --- | --- |
| Basic (Sequential) | Customer Data → Support; both responded | Not measured | Not available (remote A2A calls) |
| Advanced (Dynamic) | Only required agent(s) | 8.5 s | < 500 |
| Parallel | Customer Data + Support → Summary | 9.5 s | ≈ 2,500 |

Context passing: Basic uses sequential ADK/A2A events; Advanced stores the routing decision in session state; Parallel saves both worker outputs through callbacks and passes them to a Summary Agent.

The Advanced Router completed its observed run 1.0 second faster than the Parallel Router (8.5 s versus 9.5 s), while using fewer than 500 tokens compared with approximately 2,500 tokens for Parallel. Parallel therefore used more than five times the reported Advanced token count. These are individual observations, not averages or a controlled apples-to-apples benchmark; the modes may have invoked different agents and performed different amounts of work.

Measurement method: I used ADK Web to inspect execution duration from query submission to the final response. For a stronger comparison, I would repeat the same query at least three times per mode, record successful end-to-end wall-clock durations, and compare median latency. Quota errors (429) and availability failures (503) should be excluded from successful-response measurements.

## Key Learnings

1. MCP standardizes tool access, while A2A enables independent specialized agents to communicate through discoverable interfaces.
1. Routing choice affects cost and behavior: dynamic selection avoided unnecessary calls, while parallel work required an additional synthesis stage and higher observed token usage.
1. Reliable agent systems require explicit context management, tracing, correct async integration, and careful handling of model quotas and failures.
## Ideas for Improvement

- Add centralized model configuration, quota-aware handling, usage metrics, and bounded retries for transient errors.
- Use structured agent outputs and explicit state passing; automate tests for permissions, routing, A2A communication, response quality, and repeatable latency comparisons.
