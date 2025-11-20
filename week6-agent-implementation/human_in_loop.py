"""
Human-in-the-Loop Agent Pattern
================================

Demonstrates how to add human oversight to autonomous agents for critical operations.

Key Concepts:
- Approval workflow for sensitive actions
- Graceful pausing and resumption
- Clear communication of pending decisions
- Audit trail of human interventions
"""

import os
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import operator
from datetime import datetime
import json

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# ============================================================================
# TOOLS (Some require human approval)
# ============================================================================

@tool
def search_database(query: str) -> str:
    """
    Search internal database for information.
    
    This is a LOW-RISK operation that doesn't require approval.
    """
    return f"Database search results for '{query}': Found 3 relevant entries."

@tool  
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Send an email to a recipient.
    
    This is a MEDIUM-RISK operation that requires approval.
    
    Args:
        recipient: Email address
        subject: Email subject line
        body: Email content
    """
    # In real implementation, this would send email
    return f"Email prepared for {recipient} with subject '{subject}'"

@tool
def delete_records(record_ids: list[str]) -> str:
    """
    Delete records from the database.
    
    This is a HIGH-RISK operation that requires approval.
    
    Args:
        record_ids: List of record IDs to delete
    """
    # In real implementation, this would delete records
    return f"Prepared to delete {len(record_ids)} records: {record_ids}"

@tool
def modify_pricing(product_id: str, new_price: float) -> str:
    """
    Modify product pricing.
    
    This is a HIGH-RISK operation that requires approval.
    
    Args:
        product_id: Product identifier
        new_price: New price in dollars
    """
    return f"Prepared to change price for {product_id} to ${new_price}"

# ============================================================================
# RISK ASSESSMENT
# ============================================================================

TOOL_RISK_LEVELS = {
    "search_database": "low",
    "send_email": "medium", 
    "delete_records": "high",
    "modify_pricing": "high"
}

def requires_approval(tool_name: str) -> bool:
    """Determine if a tool requires human approval"""
    risk = TOOL_RISK_LEVELS.get(tool_name, "high")
    return risk in ["medium", "high"]

def get_risk_level(tool_name: str) -> str:
    """Get the risk level of a tool"""
    return TOOL_RISK_LEVELS.get(tool_name, "high")

# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """State for human-in-the-loop agent"""
    messages: Annotated[list, operator.add]
    pending_action: dict | None  # Action waiting for approval
    approval_granted: bool
    approval_message: str
    iteration_count: int
    audit_log: Annotated[list, operator.add]

# ============================================================================
# AGENT NODES
# ============================================================================

def agent_node(state: AgentState) -> dict:
    """
    Main agent decision-making node.
    
    Decides what action to take based on user query.
    """
    messages = state["messages"]
    
    # Bind tools to LLM
    tools = [search_database, send_email, delete_records, modify_pricing]
    llm_with_tools = llm.bind_tools(tools)
    
    # Get LLM response
    response = llm_with_tools.invoke(messages)
    
    return {
        "messages": [response],
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def check_approval_needed(state: AgentState) -> dict:
    """
    Check if the last message requires human approval.
    
    If tool call is high/medium risk, prepare approval request.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check if message has tool calls
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"pending_action": None}
    
    # Get first tool call
    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    
    # Check if approval needed
    if requires_approval(tool_name):
        risk_level = get_risk_level(tool_name)
        
        pending_action = {
            "tool_name": tool_name,
            "tool_args": tool_call["args"],
            "tool_call_id": tool_call["id"],
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to audit log
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "approval_requested",
            "tool": tool_name,
            "risk": risk_level,
            "args": tool_call["args"]
        }
        
        return {
            "pending_action": pending_action,
            "audit_log": [audit_entry]
        }
    
    return {"pending_action": None}

def request_human_approval(state: AgentState) -> dict:
    """
    Request human approval for pending action.
    
    This node pauses execution and waits for human input.
    """
    pending = state["pending_action"]
    
    print("\n" + "="*70)
    print("⚠️  HUMAN APPROVAL REQUIRED")
    print("="*70)
    print(f"Tool: {pending['tool_name']}")
    print(f"Risk Level: {pending['risk_level'].upper()}")
    print(f"Arguments:")
    for key, value in pending["tool_args"].items():
        print(f"  - {key}: {value}")
    print("="*70)
    
    # In real implementation, this would integrate with:
    # - Slack notifications
    # - Email alerts
    # - Web dashboard
    # - Mobile app
    
    approval_input = input("\nApprove this action? (yes/no/modify): ").strip().lower()
    
    if approval_input == "yes":
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "approval_granted",
            "tool": pending["tool_name"]
        }
        return {
            "approval_granted": True,
            "approval_message": "Approved by human operator",
            "audit_log": [audit_entry]
        }
    elif approval_input == "modify":
        print("\nModification not implemented in this demo.")
        print("In production, this would allow editing tool arguments.")
        return {
            "approval_granted": False,
            "approval_message": "Action rejected - modification requested",
            "pending_action": None
        }
    else:
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "approval_denied",
            "tool": pending["tool_name"],
            "reason": "Human operator rejected"
        }
        return {
            "approval_granted": False,
            "approval_message": "Action rejected by human operator",
            "pending_action": None,
            "audit_log": [audit_entry]
        }

def execute_approved_action(state: AgentState) -> dict:
    """
    Execute the approved action.
    """
    pending = state["pending_action"]
    tool_name = pending["tool_name"]
    tool_args = pending["tool_args"]
    
    # Map tool names to actual functions
    tool_map = {
        "search_database": search_database,
        "send_email": send_email,
        "delete_records": delete_records,
        "modify_pricing": modify_pricing
    }
    
    # Execute the tool
    tool_func = tool_map[tool_name]
    result = tool_func.invoke(tool_args)
    
    # Create tool message
    from langchain_core.messages import ToolMessage
    tool_message = ToolMessage(
        content=str(result),
        tool_call_id=pending["tool_call_id"]
    )
    
    # Add to audit log
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "action_executed",
        "tool": tool_name,
        "result": str(result)
    }
    
    return {
        "messages": [tool_message],
        "pending_action": None,
        "approval_granted": False,
        "audit_log": [audit_entry]
    }

def handle_rejection(state: AgentState) -> dict:
    """
    Handle rejected action.
    """
    pending = state.get("pending_action")
    approval_msg = state.get("approval_message", "Action was rejected")
    
    # Create message to inform LLM
    rejection_message = HumanMessage(
        content=f"The requested action was not approved. {approval_msg}. Please suggest an alternative approach."
    )
    
    return {
        "messages": [rejection_message],
        "pending_action": None,
        "approval_granted": False
    }

def auto_execute_low_risk(state: AgentState) -> dict:
    """
    Automatically execute low-risk actions without approval.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {}
    
    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    
    # Execute low-risk tools
    if tool_name == "search_database":
        result = search_database.invoke(tool_call["args"])
        
        from langchain_core.messages import ToolMessage
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        )
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "auto_executed",
            "tool": tool_name,
            "risk": "low"
        }
        
        return {
            "messages": [tool_message],
            "audit_log": [audit_entry]
        }
    
    return {}

# ============================================================================
# ROUTING FUNCTIONS
# ============================================================================

def should_continue(state: AgentState) -> Literal["check_approval", "end"]:
    """
    Determine if agent should continue or end.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check iteration limit
    if state.get("iteration_count", 0) >= 10:
        return "end"
    
    # If no tool calls, we're done
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return "end"
    
    return "check_approval"

def route_approval(state: AgentState) -> Literal["request_approval", "auto_execute", "agent"]:
    """
    Route based on whether approval is needed.
    """
    pending = state.get("pending_action")
    
    if pending:
        # High/medium risk - need approval
        return "request_approval"
    
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        # Low risk - auto execute
        return "auto_execute"
    
    # No action needed, continue
    return "agent"

def route_after_approval(state: AgentState) -> Literal["execute", "reject"]:
    """
    Route based on approval decision.
    """
    if state.get("approval_granted"):
        return "execute"
    return "reject"

# ============================================================================
# BUILD GRAPH
# ============================================================================

def create_human_in_loop_agent():
    """
    Create agent with human-in-the-loop approval workflow.
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("check_approval", check_approval_needed)
    workflow.add_node("request_approval", request_human_approval)
    workflow.add_node("execute", execute_approved_action)
    workflow.add_node("reject", handle_rejection)
    workflow.add_node("auto_execute", auto_execute_low_risk)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "check_approval": "check_approval",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "check_approval",
        route_approval,
        {
            "request_approval": "request_approval",
            "auto_execute": "auto_execute",
            "agent": "agent"
        }
    )
    
    workflow.add_conditional_edges(
        "request_approval",
        route_after_approval,
        {
            "execute": "execute",
            "reject": "reject"
        }
    )
    
    workflow.add_edge("execute", "agent")
    workflow.add_edge("reject", "agent")
    workflow.add_edge("auto_execute", "agent")
    
    # Add memory for persistence
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_low_risk():
    """Example: Low-risk query (auto-approved)"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Low-Risk Query (Auto-Approved)")
    print("="*70)
    
    agent = create_human_in_loop_agent()
    
    config = {"configurable": {"thread_id": "example1"}}
    
    result = agent.invoke(
        {
            "messages": [HumanMessage(content="Search the database for customer records")],
            "iteration_count": 0,
            "approval_granted": False,
            "approval_message": "",
            "pending_action": None,
            "audit_log": []
        },
        config=config
    )
    
    print("\n📋 Final Response:")
    print(result["messages"][-1].content)
    
    print("\n📊 Audit Log:")
    for entry in result["audit_log"]:
        print(f"  [{entry['timestamp']}] {entry['event']}: {entry.get('tool', 'N/A')}")

def example_medium_risk():
    """Example: Medium-risk action (requires approval)"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Medium-Risk Action (Requires Approval)")
    print("="*70)
    
    agent = create_human_in_loop_agent()
    
    config = {"configurable": {"thread_id": "example2"}}
    
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(content="Send an email to john@example.com about the quarterly report")
            ],
            "iteration_count": 0,
            "approval_granted": False,
            "approval_message": "",
            "pending_action": None,
            "audit_log": []
        },
        config=config
    )
    
    print("\n📋 Final Response:")
    if result["messages"]:
        print(result["messages"][-1].content)
    
    print("\n📊 Audit Log:")
    for entry in result["audit_log"]:
        print(f"  [{entry['timestamp']}] {entry['event']}: {entry.get('tool', 'N/A')}")

def example_high_risk():
    """Example: High-risk action (requires approval)"""
    print("\n" + "="*70)
    print("EXAMPLE 3: High-Risk Action (Requires Approval)")
    print("="*70)
    
    agent = create_human_in_loop_agent()
    
    config = {"configurable": {"thread_id": "example3"}}
    
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(content="Delete records with IDs: REC001, REC002, REC003")
            ],
            "iteration_count": 0,
            "approval_granted": False,
            "approval_message": "",
            "pending_action": None,
            "audit_log": []
        },
        config=config
    )
    
    print("\n📋 Final Response:")
    if result["messages"]:
        print(result["messages"][-1].content)
    
    print("\n📊 Audit Log:")
    for entry in result["audit_log"]:
        print(f"  [{entry['timestamp']}] {entry['event']}: {entry.get('tool', 'N/A')}")

# ============================================================================
# VISUALIZATION
# ============================================================================

def visualize_graph():
    """Generate visualization of the human-in-the-loop graph"""
    agent = create_human_in_loop_agent()
    
    try:
        from IPython.display import Image, display
        display(Image(agent.get_graph().draw_mermaid_png()))
    except Exception as e:
        print("Visualization requires IPython and graphviz")
        print(f"Error: {e}")
        
        # Print text representation
        print("\nGraph Structure:")
        print("===============")
        print("1. agent → [check_approval OR end]")
        print("2. check_approval → [request_approval OR auto_execute OR agent]")
        print("3. request_approval → [execute OR reject]")
        print("4. execute → agent")
        print("5. reject → agent")
        print("6. auto_execute → agent")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("HUMAN-IN-THE-LOOP AGENT DEMONSTRATION")
    print("="*70)
    print("\nThis demo shows how to add human approval to agent workflows.")
    print("Try running different examples to see approval in action!")
    print("\nRisk Levels:")
    print("  🟢 LOW    - Auto-approved (e.g., database search)")
    print("  🟡 MEDIUM - Requires approval (e.g., send email)")  
    print("  🔴 HIGH   - Requires approval (e.g., delete records, modify pricing)")
    
    # Run examples
    choice = input("\nWhich example? (1=low-risk, 2=medium-risk, 3=high-risk, v=visualize): ").strip()
    
    if choice == "1":
        example_low_risk()
    elif choice == "2":
        example_medium_risk()
    elif choice == "3":
        example_high_risk()
    elif choice == "v":
        visualize_graph()
    else:
        print("Invalid choice. Run script again with 1, 2, 3, or v")
