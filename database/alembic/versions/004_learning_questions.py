"""add transcript-derived learning questions"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_learning_questions"
down_revision: Union[str, None] = "003_topics_key_context"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "learning_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("video_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("videos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_sec", sa.Float(), nullable=False),
        sa.Column("end_sec", sa.Float(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("hint", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_learning_questions_video_id", "learning_questions", ["video_id"])
    op.create_index("ix_learning_questions_topic_id", "learning_questions", ["topic_id"])


def downgrade() -> None:
    op.drop_index("ix_learning_questions_topic_id", table_name="learning_questions")
    op.drop_index("ix_learning_questions_video_id", table_name="learning_questions")
    op.drop_table("learning_questions")