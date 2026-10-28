CREATE TABLE IF NOT EXISTS review_events (
 id uuid PRIMARY KEY, version_id uuid NOT NULL REFERENCES versions(id),
 actor_id text NOT NULL, status text NOT NULL, metadata jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO knowledge_schema(version) VALUES(2) ON CONFLICT DO NOTHING;
