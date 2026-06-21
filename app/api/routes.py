from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.agent.graph import agent
from app.db.database import get_db
from app.db.models import ComplianceAudit

router = APIRouter()


# --- Request/Response Models ---

class ScanRequest(BaseModel):
    system_name: str
    system_description: str


class HumanReviewRequest(BaseModel):
    decision: str  # APPROVED or REJECTED
    comments: Optional[str] = None


# --- Endpoints ---

@router.post("/scan")
def scan_system(request: ScanRequest):
    """Submit an AI system for EU AI Act compliance scanning."""

    initial_state = {
        "system_name": request.system_name,
        "system_description": request.system_description,
        "risk_category": None,
        "risk_reasoning": None,
        "compliance_gaps": None,
        "audit_document": None,
        "agent_reasoning": [],
        "audit_id": None,
        "status": None,
        "human_decision": None,
        "human_comments": None
    }

    result = agent.invoke(initial_state)

    return {
        "audit_id": result["audit_id"],
        "system_name": result["system_name"],
        "risk_category": result["risk_category"],
        "compliance_gaps": result["compliance_gaps"],
        "status": result["status"],
        "message": "Scan complete. Audit is pending human review."
    }


@router.get("/audit/{audit_id}")
def get_audit(audit_id: str, db: Session = Depends(get_db)):
    """Get full audit details by ID."""

    audit = db.query(ComplianceAudit).filter(ComplianceAudit.id == audit_id).first()

    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    return {
        "audit_id": audit.id,
        "system_name": audit.system_name,
        "system_description": audit.system_description,
        "risk_category": audit.risk_category,
        "compliance_gaps": audit.compliance_gaps,
        "audit_document": audit.audit_document,
        "status": audit.status,
        "human_decision": audit.human_decision,
        "human_comments": audit.human_comments,
        "agent_reasoning": audit.agent_reasoning,
        "created_at": audit.created_at
    }


@router.post("/audit/{audit_id}/review")
def review_audit(audit_id: str, request: HumanReviewRequest, db: Session = Depends(get_db)):
    """Human-in-the-loop: approve or reject an audit."""

    if request.decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decision must be APPROVED or REJECTED")

    audit = db.query(ComplianceAudit).filter(ComplianceAudit.id == audit_id).first()

    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    if audit.status not in ["PENDING", "PENDING_HUMAN_REVIEW"]:
        raise HTTPException(status_code=400, detail=f"Audit is already {audit.status}")

    audit.status = request.decision
    audit.human_decision = request.decision
    audit.human_comments = request.comments
    audit.reviewed_at = datetime.utcnow()

    db.commit()

    return {
        "audit_id": audit_id,
        "decision": request.decision,
        "comments": request.comments,
        "message": f"Audit has been {request.decision}"
    }


@router.get("/audits")
def list_audits(db: Session = Depends(get_db)):
    """List all audits with their current status."""

    audits = db.query(ComplianceAudit).order_by(ComplianceAudit.created_at.desc()).all()

    return [
        {
            "audit_id": a.id,
            "system_name": a.system_name,
            "risk_category": a.risk_category,
            "status": a.status,
            "created_at": a.created_at
        }
        for a in audits
    ]