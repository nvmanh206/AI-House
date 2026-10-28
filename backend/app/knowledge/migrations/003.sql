ALTER TABLE documents ADD COLUMN IF NOT EXISTS observed_hash text;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS fetched_at timestamptz;
INSERT INTO knowledge_schema(version) VALUES(3) ON CONFLICT DO NOTHING;
