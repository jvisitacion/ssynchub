-- Sync Hub schema
-- Run automatically on first app launch via DatabaseConnection.initialize_schema()

CREATE TABLE IF NOT EXISTS projects (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    created_at  TIMESTAMPTZ  DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS content_items (
    id              SERIAL PRIMARY KEY,
    content_type    VARCHAR(50)  NOT NULL,
    title           VARCHAR(255) NOT NULL DEFAULT 'Untitled',
    text_content    TEXT         DEFAULT '',
    diagram_data    JSONB        DEFAULT '{}',
    attachment_path TEXT         DEFAULT NULL,
    created_at      TIMESTAMPTZ  DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app_settings (
    setting_key   VARCHAR(100) PRIMARY KEY,
    setting_value TEXT         NOT NULL,
    updated_at    TIMESTAMPTZ  DEFAULT NOW()
);

INSERT INTO app_settings (setting_key, setting_value)
VALUES ('theme', 'dark')
ON CONFLICT (setting_key) DO NOTHING;

-- Migration: link content to projects
ALTER TABLE content_items
    ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE;

INSERT INTO projects (name)
SELECT 'Default Project'
WHERE NOT EXISTS (SELECT 1 FROM projects)
  AND EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_name = 'content_items' AND column_name = 'project_id'
  )
  AND EXISTS (SELECT 1 FROM content_items WHERE project_id IS NULL);

UPDATE content_items
SET project_id = (SELECT id FROM projects ORDER BY id LIMIT 1)
WHERE project_id IS NULL
  AND EXISTS (SELECT 1 FROM projects);

-- Keep only the latest row per project + section before adding uniqueness
DELETE FROM content_items older
USING content_items newer
WHERE older.project_id = newer.project_id
  AND older.content_type = newer.content_type
  AND older.project_id IS NOT NULL
  AND (
      older.updated_at < newer.updated_at
      OR (older.updated_at = newer.updated_at AND older.id < newer.id)
  );

CREATE UNIQUE INDEX IF NOT EXISTS uq_content_items_project_type
    ON content_items (project_id, content_type);

CREATE INDEX IF NOT EXISTS idx_content_items_type
    ON content_items (content_type);

CREATE INDEX IF NOT EXISTS idx_content_items_project_type
    ON content_items (project_id, content_type);

-- Seed missing sections for existing projects
INSERT INTO content_items (project_id, content_type, title)
SELECT p.id, v.content_type, v.title
FROM projects p
CROSS JOIN (
    VALUES
        ('development_tasks', 'Development Tasks'),
        ('system_flows', 'System Flows'),
        ('backend_behavior', 'Backend Behavior'),
        ('frontend_behavior', 'Frontend Behavior'),
        ('database_logic', 'Database Logic'),
        ('debugging_ideas', 'Ideas from Debugging Session'),
        ('conversation_meeting', 'Conversation / Meeting')
) AS v(content_type, title)
WHERE NOT EXISTS (
    SELECT 1 FROM content_items ci
    WHERE ci.project_id = p.id AND ci.content_type = v.content_type
);
