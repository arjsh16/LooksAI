"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id',              sa.Integer(),     primary_key=True),
        sa.Column('email',           sa.String(255),   nullable=False, unique=True),
        sa.Column('username',        sa.String(100),   nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255),   nullable=False),
        sa.Column('is_active',       sa.Boolean(),     server_default='true'),
        sa.Column('is_verified',     sa.Boolean(),     server_default='false'),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_users_email',    'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])

    # Analysis sessions
    analysis_status = postgresql.ENUM(
        'pending', 'processing', 'completed', 'failed',
        name='analysis_status'
    )
    analysis_status.create(op.get_bind())

    op.create_table(
        'analysis_sessions',
        sa.Column('id',              sa.Integer(),     primary_key=True),
        sa.Column('user_id',         sa.Integer(),     sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status',          sa.Enum('pending', 'processing', 'completed', 'failed', name='analysis_status'), server_default='pending'),
        sa.Column('image_front',     sa.String(500)),
        sa.Column('image_left',      sa.String(500)),
        sa.Column('image_right',     sa.String(500)),
        sa.Column('face_shape',      sa.String(50)),
        sa.Column('skin_analysis',   postgresql.JSONB),
        sa.Column('facial_features', postgresql.JSONB),
        sa.Column('landmarks_data',  postgresql.JSONB),
        sa.Column('error_message',   sa.Text()),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at',    sa.DateTime(timezone=True)),
    )
    op.create_index('idx_sessions_user_id',    'analysis_sessions', ['user_id'])
    op.create_index('idx_sessions_status',     'analysis_sessions', ['status'])
    op.create_index('idx_sessions_created_at', 'analysis_sessions', ['created_at'])

    # Recommendations
    op.create_table(
        'recommendations',
        sa.Column('id',                     sa.Integer(),   primary_key=True),
        sa.Column('session_id',             sa.Integer(),   sa.ForeignKey('analysis_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('maintenance_preference', sa.String(10)),
        sa.Column('length_preference',      sa.String(10)),
        sa.Column('filtered_haircuts',      postgresql.JSONB),
        sa.Column('narrative',              sa.Text()),
        sa.Column('haircut_table_md',       sa.Text()),
        sa.Column('skincare_tips',          sa.Text()),
        sa.Column('lifestyle_tips',         sa.Text()),
        sa.Column('created_at',             sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_recs_session_id', 'recommendations', ['session_id'])

    # Chat messages
    message_role = postgresql.ENUM('user', 'assistant', 'system', name='message_role')
    message_role.create(op.get_bind())

    op.create_table(
        'chat_messages',
        sa.Column('id',         sa.Integer(),   primary_key=True),
        sa.Column('session_id', sa.Integer(),   sa.ForeignKey('analysis_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role',       sa.Enum('user', 'assistant', 'system', name='message_role'), nullable=False),
        sa.Column('content',    sa.Text(),      nullable=False),
        sa.Column('meta',       postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_chat_session_id',  'chat_messages', ['session_id'])
    op.create_index('idx_chat_created_at',  'chat_messages', ['created_at'])


def downgrade() -> None:
    op.drop_table('chat_messages')
    op.drop_table('recommendations')
    op.drop_table('analysis_sessions')
    op.drop_table('users')
    postgresql.ENUM(name='message_role').drop(op.get_bind())
    postgresql.ENUM(name='analysis_status').drop(op.get_bind())
