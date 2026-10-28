CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE TABLE IF NOT EXISTS knowledge_schema (version integer PRIMARY KEY);
CREATE TABLE IF NOT EXISTS sources (
 id uuid PRIMARY KEY,name text NOT NULL,domains jsonb NOT NULL,seeds jsonb NOT NULL,
 topic text NOT NULL CHECK(topic IN ('PRICES','GUIDANCE','REGULATIONS')),
 enabled boolean NOT NULL DEFAULT true,interval_hours integer NOT NULL,
 checked_at timestamptz,created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS crawl_runs (
 id uuid PRIMARY KEY,source_id uuid NOT NULL REFERENCES sources(id),
 status text NOT NULL CHECK(status IN ('QUEUED','RUNNING','SUCCEEDED','PARTIAL','FAILED')),
 created_at timestamptz NOT NULL DEFAULT now(),started_at timestamptz,finished_at timestamptz,
 processed integer NOT NULL DEFAULT 0,changed integer NOT NULL DEFAULT 0,errors jsonb NOT NULL DEFAULT '[]'
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_crawl ON crawl_runs(source_id) WHERE status IN ('QUEUED','RUNNING');
CREATE TABLE IF NOT EXISTS documents (
 id uuid PRIMARY KEY,source_id uuid NOT NULL REFERENCES sources(id),url text NOT NULL UNIQUE,
 title text NOT NULL,active_version uuid,checked_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS versions (
 id uuid PRIMARY KEY,document_id uuid NOT NULL REFERENCES documents(id),content_hash text NOT NULL,
 status text NOT NULL CHECK(status IN ('PUBLISHED','PENDING_REVIEW','BLOCKED','SUPERSEDED')),
 content text NOT NULL,raw_path text NOT NULL,metadata jsonb NOT NULL,
 embedding_model text NOT NULL,created_at timestamptz NOT NULL DEFAULT now(),UNIQUE(document_id,content_hash)
);
CREATE TABLE IF NOT EXISTS chunks (
 id uuid PRIMARY KEY,version_id uuid NOT NULL REFERENCES versions(id),position integer NOT NULL,
 content text NOT NULL,search tsvector NOT NULL,embedding vector(768) NOT NULL,UNIQUE(version_id,position)
);
CREATE INDEX IF NOT EXISTS chunks_search ON chunks USING gin(search);
CREATE INDEX IF NOT EXISTS chunks_vector ON chunks USING hnsw(embedding vector_cosine_ops);
CREATE TABLE IF NOT EXISTS retrieval_logs (
 id uuid PRIMARY KEY,created_at timestamptz NOT NULL DEFAULT now(),mode text NOT NULL,chunk_ids jsonb NOT NULL,elapsed_ms integer NOT NULL
);
INSERT INTO knowledge_schema(version) VALUES(1) ON CONFLICT DO NOTHING;
