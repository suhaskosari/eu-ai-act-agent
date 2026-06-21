from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass


class ComplianceAudit(Base):
    __tablename__ = "compliance_audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    system_name = Column(String(255), nullable=False)
    system_description = Column(Text, nullable=False)
    risk_category = Column(String(100))        # e.g. HIGH, LIMITED, MINIMAL
    compliance_gaps = Column(JSON)             # list of gaps found
    audit_document = Column(Text)             # generated audit report
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    human_decision = Column(String(50))        # set when human reviews
    human_comments = Column(Text)             # optional reviewer notes
    agent_reasoning = Column(JSON)            # full reasoning trace
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)