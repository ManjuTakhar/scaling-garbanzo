from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from app.db.base import Base


class GitLink(Base):
    """
    Stores links between a local issue and Git artifacts (GH issue, PR, branch),
    optionally tied to a GitHub App installation context.
    """
    __tablename__ = "git_links"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Your local app identifiers
    local_issue_id = Column(
        String,
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Provider + repo info
    provider = Column(String, nullable=False, default="github", index=True)  # e.g., "github"
    repository = Column(String, nullable=False, index=True)                  # "owner/repo"

    # Optional installation / org context (no FK to avoid mapper traps)
    installation_id = Column(Integer, nullable=True, index=True)  # GitHub App installation id
    account_login = Column(String, nullable=True, index=True)     # org/user login (e.g., "my-org")

    # GitHub references
    github_issue_number = Column(Integer, nullable=True)          # e.g., 123
    github_issue_url = Column(Text, nullable=True)
    pr_number = Column(Integer, nullable=True)
    branch_name = Column(String, nullable=True)

    # Optional extra data
    meta = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        # Useful indexes / (soft) uniqueness guard for GH issues in a repo
        Index("ix_git_links_repo_issue", "repository", "github_issue_number"),
        Index("ix_git_links_repo_pr", "repository", "pr_number"),
        # In Postgres/SQLite, UNIQUE with NULL allows multiple NULLs (so safe for rows without numbers)
        Index(
            "uq_gitlink_provider_repo_issue",
            "provider",
            "repository",
            "github_issue_number",
            unique=True,
        ),
    )


