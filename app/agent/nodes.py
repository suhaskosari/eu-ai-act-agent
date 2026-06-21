from langchain_ollama import OllamaLLM
from app.agent.state import AgentState
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

llm = OllamaLLM(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    model=os.getenv("OLLAMA_MODEL", "llama3.2")
)


def classify_risk(state: AgentState) -> AgentState:
    """Node 1: Classify the AI system under EU AI Act risk categories."""

    prompt = f"""You are an EU AI Act compliance expert.

Classify this AI system into one of these risk categories:
- UNACCEPTABLE: Systems that are banned (e.g. social scoring, real-time biometric surveillance)
- HIGH: Systems in critical areas (e.g. hiring, credit scoring, medical, law enforcement, education)
- LIMITED: Systems with transparency obligations (e.g. chatbots, deepfakes)
- MINIMAL: Everything else (e.g. spam filters, recommendation systems)

AI System Name: {state['system_name']}
AI System Description: {state['system_description']}

Respond in this exact format:
CATEGORY: <one of UNACCEPTABLE/HIGH/LIMITED/MINIMAL>
REASONING: <2-3 sentences explaining why>"""

    response = llm.invoke(prompt)
    lines = response.strip().split('\n')

    category = "MINIMAL"
    reasoning = response

    for line in lines:
        if line.startswith("CATEGORY:"):
            category = line.replace("CATEGORY:", "").strip()
        if line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()

    return {
        **state,
        "risk_category": category,
        "risk_reasoning": reasoning,
        "agent_reasoning": [f"Risk classification: {category} — {reasoning}"]
    }


def scan_compliance_gaps(state: AgentState) -> AgentState:
    """Node 2: Identify specific compliance gaps based on risk category."""

    prompt = f"""You are an EU AI Act compliance auditor.

The AI system below has been classified as {state['risk_category']} risk.

AI System Name: {state['system_name']}
AI System Description: {state['system_description']}

Based on the EU AI Act requirements for {state['risk_category']} risk systems, list the compliance gaps.
Focus on:
- Data governance requirements
- Transparency obligations
- Human oversight mechanisms
- Technical documentation
- Logging and auditability

List each gap on a new line starting with "GAP:"
If no gaps, write "GAP: None identified" """

    response = llm.invoke(prompt)
    gaps = []

    for line in response.strip().split('\n'):
        if line.startswith("GAP:"):
            gap = line.replace("GAP:", "").strip()
            if gap:
                gaps.append(gap)

    if not gaps:
        gaps = ["Unable to parse gaps — manual review required"]

    reasoning = state.get("agent_reasoning", [])
    reasoning.append(f"Compliance gaps identified: {len(gaps)} gaps found")

    return {
        **state,
        "compliance_gaps": gaps,
        "agent_reasoning": reasoning
    }


def generate_audit_document(state: AgentState) -> AgentState:
    """Node 3: Generate a formal audit-ready document."""

    gaps_text = "\n".join(f"- {g}" for g in state.get("compliance_gaps", []))

    prompt = f"""You are an EU AI Act compliance officer. Generate a formal audit document.

AI System: {state['system_name']}
Description: {state['system_description']}
Risk Category: {state['risk_category']}
Compliance Gaps:
{gaps_text}

Write a structured audit document with these sections:
1. EXECUTIVE SUMMARY
2. SYSTEM OVERVIEW
3. RISK CLASSIFICATION & JUSTIFICATION
4. COMPLIANCE GAPS IDENTIFIED
5. RECOMMENDED ACTIONS
6. CONCLUSION

Be formal, specific, and actionable."""

    audit_doc = llm.invoke(prompt)

    reasoning = state.get("agent_reasoning", [])
    reasoning.append("Audit document generated successfully")

    audit_id = str(uuid.uuid4())

    return {
        **state,
        "audit_document": audit_doc,
        "audit_id": audit_id,
        "status": "PENDING",
        "agent_reasoning": reasoning
    }


def save_to_database(state: AgentState) -> AgentState:
    """Node 4: Save the audit to PostgreSQL and wait for human review."""
    from app.db.database import SessionLocal
    from app.db.models import ComplianceAudit

    db = SessionLocal()
    try:
        audit = ComplianceAudit(
            id=state["audit_id"],
            system_name=state["system_name"],
            system_description=state["system_description"],
            risk_category=state["risk_category"],
            compliance_gaps=state["compliance_gaps"],
            audit_document=state["audit_document"],
            status="PENDING",
            agent_reasoning=state["agent_reasoning"]
        )
        db.add(audit)
        db.commit()
    finally:
        db.close()

    return {
        **state,
        "status": "PENDING_HUMAN_REVIEW"
    }