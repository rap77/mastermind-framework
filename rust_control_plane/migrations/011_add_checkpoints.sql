-- Hybrid table: relational identity + JSONB payload
-- Required by: context-projection objective
CREATE TABLE checkpoints (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id  UUID,                         -- nullable: no projects table yet
    task_id     TEXT        NOT NULL,          -- MM task id, e.g. "T1" (TEXT, not FK)
    session_id  UUID        NOT NULL,
    resume_state JSONB      NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_checkpoints_task_id    ON checkpoints (task_id);
CREATE INDEX idx_checkpoints_session_id ON checkpoints (session_id);
CREATE INDEX idx_checkpoints_created_at ON checkpoints (created_at);
