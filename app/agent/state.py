from typing import TypedDict, Optional, List


class AgentState(TypedDict):
    # Input
    system_name: str
    system_description: str

    # Agent outputs (filled as agent runs)
    risk_category: Optional[str]
    risk_reasoning: Optional[str]
    compliance_gaps: Optional[List[str]]
    audit_document: Optional[str]
    agent_reasoning: Optional[List[str]]

    # Human-in-the-loop
    audit_id: Optional[str]
    status: Optional[str]
    human_decision: Optional[str]
    human_comments: Optional[str]