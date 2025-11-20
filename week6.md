# Week 6: Agent-Based AI Systems

Welcome to Week 6 of AI Coding Essentials! This week, you'll design and implement autonomous AI agents that can perform complex tasks through planning, tool use, and decision-making. You'll learn to build agents that go beyond simple workflows to handle open-ended problems with multiple possible approaches.

## Learning Objectives

By the end of this week, you will be able to:
- Understand the difference between simple LLMs, AI workflows, and autonomous agents
- Design effective agent architectures using proven patterns (augmented LLM, prompt chaining, routing, orchestrator-workers, evaluator-optimizer)
- Implement custom tools for agents to interact with external systems
- Build multi-agent systems with specialized roles and clear communication patterns
- Apply testing strategies specific to non-deterministic agent behaviors
- Choose appropriate agent frameworks (Google ADK, LangGraph, Vercel AI SDK) for your use case
- Implement safety, alignment, and ethical considerations in agent design

## Lecture: AI Agents - From Simple Automation to Intelligent Systems

This lecture introduces the fundamental concepts of AI agents and provides practical guidance on building production-ready agent systems. We'll explore when to use agents versus simpler approaches, examine five core design patterns, and dive deep into three major agent development frameworks.

- **[View the Slides](./slides/6-agents-export.pdf)** - Complete slide deck in PDF format

## Week 6 Exercises

### Exercise 1: Anthropic's Multi-Agent Research System Analysis
**Objective**: Analyze a real-world multi-agent system implementation to understand enterprise-scale agent architecture patterns

**Tasks**:
1. Read [Anthropic's engineering post](https://www.anthropic.com/engineering/built-multi-agent-research-system) about their multi-agent research system
2. Read [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) for foundational agent design principles
3. Review the [Anthropic Agent Patterns Cookbook](https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/README.md) for practical implementation examples
4. Identify the key architectural components and how they interact
5. Analyze the agent coordination patterns and communication strategies

### Exercise 2: Build Your First Agent (Choose Your Framework)
**Objective**: Get hands-on experience building an agent using one of the production frameworks covered in the lecture

**Choose one of the following frameworks and complete the corresponding tasks:**

#### Option A: Google ADK (Python)
- **Documentation**: [google.github.io/adk-docs](https://google.github.io/adk-docs/)
- **Setup**: `pip install google-adk`
- **Build**: Create an agent that can search the web and summarize results
- **Test**: Use `adk web` for the development UI

#### Option B: LangGraph (Python)
- **Documentation**: [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/)
- **Setup**: `pip install -U langgraph`
- **Build**: Create a stateful agent with memory that can have multi-turn conversations
- **Test**: Use LangSmith for debugging and visualization

#### Option C: Vercel AI SDK (TypeScript)
- **Documentation**: [ai-sdk.dev](https://ai-sdk.dev/)
- **Setup**: `npm install ai`
- **Build**: Create a web-based agent with tool calling capabilities
- **Test**: Implement streaming responses in a simple UI

**All options should implement:**
1. At least one tool function (e.g., weather lookup, calculation, search)
2. Proper error handling and timeout management
3. Clear logging of the agent's decision-making process
4. A simple test scenario demonstrating the agent's capabilities

### Optional Exercises
1. **[Code Reviewer Agent Demo](https://github.com/ai-powerup-oct-25/agent-demo)** - Reference implementation of a code reviewer agent using Google ADK. Explore the code to see how custom tools and agent architecture work in practice.

2. **Agent Testing Framework** - Design comprehensive testing for your agent:
   - Unit tests for individual tools
   - Integration tests for agent-tool interactions
   - LLM-as-judge evaluations for output quality

3. [Continue Your Personal Project](./exercises/plan-your-personal-project.md) - Add agent capabilities to your ongoing project

4. **Agent Pattern Comparison** - Implement the same task using different patterns (augmented LLM vs. orchestrator-workers) and compare effectiveness

## Weekly Tasks

- [ ] Review the slides:
  - [ ] [AI Agents Slides](./slides/6-agents-export.pdf)
- [ ] Attend or watch the live Q&A session
- [ ] Complete Exercise 1: Read and analyze Anthropic's multi-agent research system
- [ ] Complete Exercise 2: Build your first agent using Google ADK, LangGraph, or Vercel AI SDK
- [ ] Apply what you've learned to your personal project

### Optional
- [ ] Explore the [Code Reviewer Agent Demo](https://github.com/ai-powerup-oct-25/agent-demo) to see a reference implementation
- [ ] Build and compare multiple agent patterns for the same task
- [ ] Implement comprehensive testing suite for your agent
- [ ] Explore advanced features (human-in-the-loop, multi-agent coordination, safety guardrails)
- [ ] Share your agent implementation in the [#show-and-tell Discord channel](https://discord.com/channels/690141234596937780/1427499665812881518)

## Key Concepts Covered

- **Agent Fundamentals**: Understanding when to use agents vs. workflows vs. simple LLMs
- **Design Patterns**:
  - **Augmented LLM**: Enhanced with retrieval, tools, and memory
  - **Prompt Chaining**: Sequential steps with structured handoffs
  - **Routing**: Classify inputs and direct to specialists
  - **Orchestrator-Workers**: Dynamic task breakdown and delegation
  - **Evaluator-Optimizer**: Iterative refinement with feedback loops
- **Tool Integration**: Creating and connecting external capabilities to agents
- **Multi-Agent Systems**: Coordination strategies for specialized agents working together
- **Testing Strategies**: Handling non-deterministic behavior, LLM-as-judge, end-state evaluation
- **Safety & Ethics**: Implementing guardrails, human oversight, and ethical considerations
- **Performance Monitoring**: Token usage, latency tracking, cost optimization

## Agent Frameworks Comparison

### Google ADK (Agent Development Kit)
- **Language**: Python & Java
- **Best For**: Production deployment, Google Cloud integration, enterprise features
- **Key Features**: Model-agnostic, built-in evaluation, Vertex AI deployment
- **Get Started**: `pip install google-adk` then `adk web` for development UI

### LangGraph
- **Language**: Python
- **Best For**: Stateful, long-running agent workflows with complex orchestration
- **Key Features**: Graph-based architecture, persistent checkpoints, human-in-the-loop, LangSmith debugging
- **Get Started**: `pip install -U langgraph`

### Vercel AI SDK
- **Language**: TypeScript
- **Best For**: Web developers building AI-powered applications with React/Next.js
- **Key Features**: Framework-agnostic, streaming support, type-safe with Zod, multi-provider API
- **Get Started**: `npm install ai` or visit [ai-sdk.dev](https://ai-sdk.dev/)

## Testing Agents: Key Challenges

### Common Testing Pitfalls
- **Non-deterministic behavior** makes reproducibility difficult
- **Compounding errors** in multi-step workflows
- **Context drift** over long conversations
- **Tool interaction complexity** creates edge cases

### Mitigation Strategies
- **Temperature control** for more consistent outputs
- **Checkpoint systems** for error recovery
- **LLM-as-judge** for evaluating complex outputs
- **End-state testing** - focus on outcomes, not intermediate steps
- **Small sample testing** for rapid iteration

## Safety and Ethical Considerations

- **Guardrails**: Prevent harmful or unintended actions
- **Human Oversight**: Critical decisions require human approval
- **Transparency**: Make reasoning and planning steps visible
- **Clear Boundaries**: Define what agents can and cannot do
- **Error Recovery**: Graceful handling of failures with user-friendly messages
- **Cost Management**: Monitor token usage and implement budgets

## Design Principles from Anthropic

1. **Start Simple** - Only add complexity when it demonstrably improves outcomes
2. **Maintain Transparency** - Make agent reasoning visible for debugging
3. **Clear Interfaces** - Document and test agent-computer interactions thoroughly
4. **Define Success Criteria** - Establish measurable objectives upfront
5. **Implement Guardrails** - Safety first with proper constraints
6. **Plan for Failure** - Robust error handling and recovery strategies

---

Remember, agents are powerful but complex tools. Start with the simplest solution that meets your needs, build incrementally, test thoroughly, and deploy with appropriate safeguards. Focus on creating clear success criteria and implementing proper error handling from the start!
