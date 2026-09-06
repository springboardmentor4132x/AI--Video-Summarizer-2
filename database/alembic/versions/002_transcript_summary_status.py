"""add transcript and summary processing status"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_transcript_summary_status"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    content_status = sa.Enum("not_started", "processing", "completed", "failed", name="content_status")
    content_status.create(op.get_bind(), checkfirst=True)
    op.add_column("transcripts", sa.Column("status", content_status, nullable=False, server_default="not_started"))
    op.add_column("transcripts", sa.Column("error_message", sa.Text(), nullable=True))
    op.create_index("ix_transcripts_status", "transcripts", ["status"])
    op.add_column("summaries", sa.Column("status", content_status, nullable=False, server_default="not_started"))
    op.add_column("summaries", sa.Column("error_message", sa.Text(), nullable=True))
    op.create_index("ix_summaries_status", "summaries", ["status"])


def downgrade() -> None:
    op.drop_index("ix_summaries_status", table_name="summaries")
    op.drop_column("summaries", "error_message")
    op.drop_column("summaries", "status")
    op.drop_index("ix_transcripts_status", table_name="transcripts")
    op.drop_column("transcripts", "error_message")
    op.drop_column("transcripts", "status")
    sa.Enum(name="content_status").drop(op.get_bind(), checkfirst=True)