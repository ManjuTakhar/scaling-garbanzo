from sqlalchemy import Column, String, Text, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.utils import generate_id
from app.db.base import Base 

class Label(Base):
    """
    Label model representing a label that can be applied to an issue.
    """
    __tablename__ = "labels"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    color = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationship to issues through issue_labels
    issues = relationship("Issue", secondary="issue_labels", back_populates="labels", lazy="joined", overlaps="issue_labels")
    issue_labels = relationship("IssueLabel", back_populates="label", lazy="joined", overlaps="issues,labels")
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = generate_id(kwargs.get('name', ''))


class IssueLabel(Base):
    """
    IssueLabel model representing a relationship between an issue and a label.
    """
    __tablename__ = "issue_labels"

    issue_id = Column(String, ForeignKey("issues.id"), primary_key=True)
    label_id = Column(String, ForeignKey("labels.id"), primary_key=True)
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationship to issues
    issue = relationship("Issue", back_populates="issue_labels", foreign_keys=[issue_id], overlaps="issues,labels")
    label = relationship("Label", back_populates="issue_labels", foreign_keys=[label_id], overlaps="issues,labels")

