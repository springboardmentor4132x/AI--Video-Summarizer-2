"""add topics and transcript context to key moments"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_topics_key_context"
down_revision: Union[str, None] = "002_transcript_summary_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("video_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("videos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_sec", sa.Float(), nullable=False),
        sa.Column("end_sec", sa.Float(), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("transcript_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_topics_video_id", "topics", ["video_id"])
    op.add_column("key_moments", sa.Column("transcript_text", sa.Text(), nullable=True))
    op.add_column("key_moments", sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id", ondelete="SET NULL"), nullable=True))
    op.create_index("ix_key_moments_topic_id", "key_moments", ["topic_id"])


def downgrade() -> None:
    op.drop_index("ix_key_moments_topic_id", table_name="key_moments")
    op.drop_column("key_moments", "topic_id")
    op.drop_column("key_moments", "transcript_text")
    op.drop_index("ix_topics_video_id", table_name="topics")
    op.drop_table("topics")