"""create database

Revision ID: 2044db86490d
Revises: 
Create Date: 2020-03-19 07:48:57.893961

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey

from conversation_core_lib.conversation_core_lib import ConversationCoreLib
from conversation_core_lib.data_layers.data.db.constants import COLUMN_CONVERSATION_MSG_SOURCE_LENGTH, COLUMN_CONVERSATION_MSG_DATA_LENGTH
from conversation_core_lib.data_layers.data.db.entities.conversation import Conversation
from conversation_core_lib.data_layers.data.db.entities.conversation_chat import ConversationChat
from conversation_core_lib.data_layers.data.db.entities.conversation_chat_settings import ConversationChatSettings
from conversation_core_lib.data_layers.data.db.entities.conversation_message import ConversationMessage
from conversation_core_lib.data_layers.data.db.entities.conversation_participant import ConversationParticipant

revision = "2044db86490d"
down_revision = None
branch_labels = None
depends_on = None

fk_last_conversation_message_id = "fk_last_conversation_message_id"


def upgrade():
    user_foreign_key = "{}.{}".format(ConversationCoreLib.link_user_table, ConversationCoreLib.link_user_column_id)

    op.create_table(
        Conversation.__tablename__,

        sa.Column(Conversation.id.key, sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column(Conversation.content.key, sa.VARCHAR(length=COLUMN_CONVERSATION_MSG_SOURCE_LENGTH), default="", nullable=False),
        sa.Column(Conversation.render_data.key, sa.VARCHAR(length=COLUMN_CONVERSATION_MSG_DATA_LENGTH), default=None, nullable=True),
        sa.Column(Conversation.information.key, sa.VARCHAR(length=255), default=""),
        sa.Column(Conversation.title.key, sa.VARCHAR(length=255), default=""),
        sa.Column(Conversation.originator_user_id.key, sa.Integer, ForeignKey(user_foreign_key)),

        sa.Column(Conversation.created_at.key, sa.DateTime, default=datetime.utcnow),
        sa.Column(Conversation.updated_at.key, sa.DateTime, default=datetime.utcnow),
        sa.Column(Conversation.deleted_at.key, sa.DateTime, default=None)
    )

    op.create_table(
        ConversationMessage.__tablename__,

        sa.Column(ConversationMessage.id.key, sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column(ConversationMessage.content.key, sa.VARCHAR(length=COLUMN_CONVERSATION_MSG_SOURCE_LENGTH)),
        sa.Column(ConversationMessage.render_data.key, sa.VARCHAR(length=COLUMN_CONVERSATION_MSG_DATA_LENGTH)),
        sa.Column(ConversationMessage.conversation_id.key, sa.Integer, ForeignKey("conversation.id")),
        sa.Column(ConversationMessage.user_id.key, sa.Integer, ForeignKey(user_foreign_key)),
        sa.Column(ConversationMessage.source.key, sa.Integer, default=ConversationMessage.MessageSource.MESSAGING),

        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime, default=None),

        sa.Index("index_conversation", "conversation_id", unique=False)
    )

    with op.batch_alter_table(Conversation.__tablename__, schema=None) as batch_op:
        batch_op.add_column(sa.Column(Conversation.last_conversation_message_id.key, sa.Integer, ForeignKey("conversation_message.id", name=fk_last_conversation_message_id), nullable=True))
    # op.add_column(Conversation.__tablename__, sa.Column(Conversation.last_conversation_message_id.key, sa.Integer, ForeignKey("conversation_message.id", name=fk_last_conversation_message_id), nullable=True))

    op.create_table(
        ConversationChat.__tablename__,

        sa.Column(ConversationChat.id.key, sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column(ConversationChat.conversation_id.key, sa.Integer, ForeignKey("conversation.id")),
        sa.Column(ConversationChat.user_id.key, sa.Integer, ForeignKey(user_foreign_key)),

        sa.Index("index_chat_user_to_conversation", "user_id", "conversation_id", unique=True)
    )

    op.create_table(
        ConversationChatSettings.__tablename__,

        sa.Column(ConversationChatSettings.id.key, sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column(ConversationChatSettings.user_id.key, sa.Integer, ForeignKey(user_foreign_key)),
        sa.Column(ConversationChatSettings.expand.key, sa.Boolean, default=False),
        sa.Column(ConversationChatSettings.conversation_expand.key, sa.Boolean, default=False),
        sa.Column(ConversationChatSettings.active_conversation_id.key, sa.Integer, nullable=True),

        sa.Index("index_user_id", "user_id", unique=True)
    )

    op.create_table(
        ConversationParticipant.__tablename__,

        sa.Column(ConversationParticipant.id.key, sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column(ConversationParticipant.read_conversation_message_id.key, sa.Integer, ForeignKey("conversation_message.id"), nullable=True, default=None),
        sa.Column(ConversationParticipant.user_active.key, sa.Boolean, nullable=False, default=False),
        sa.Column(ConversationParticipant.conversation_id.key, sa.Integer, ForeignKey("conversation.id"), nullable=False),
        sa.Column(ConversationParticipant.user_id.key, sa.Integer, ForeignKey(user_foreign_key), nullable=False),

        sa.Index("index_participant_conversation_to_user", 'conversation_id', 'user_id', unique=True),
        sa.Index("index_participant_user_to_conversation", 'user_id', 'conversation_id', unique=False)
    )


def downgrade():
    op.drop_constraint(fk_last_conversation_message_id, Conversation.__tablename__, type_="foreignkey")
    op.drop_column(Conversation.__tablename__, "last_conversation_message_id")
    op.drop_table(ConversationChat.__tablename__)
    op.drop_table(ConversationChatSettings.__tablename__)
    op.drop_table(ConversationParticipant.__tablename__)
    op.drop_table(ConversationMessage.__tablename__)
    op.drop_table(Conversation.__tablename__)