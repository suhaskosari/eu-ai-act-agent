from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    classify_risk,
    scan_compliance_gaps,
    generate_audit_document,
    save_to_database
)


def build_graph():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("classify_risk", classify_risk)
    graph.add_node("scan_compliance_gaps", scan_compliance_gaps)
    graph.add_node("generate_audit_document", generate_audit_document)
    graph.add_node("save_to_database", save_to_database)

    # Define flow
    graph.set_entry_point("classify_risk")
    graph.add_edge("classify_risk", "scan_compliance_gaps")
    graph.add_edge("scan_compliance_gaps", "generate_audit_document")
    graph.add_edge("generate_audit_document", "save_to_database")
    graph.add_edge("save_to_database", END)

    return graph.compile()


agent = build_graph()