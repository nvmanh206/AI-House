CREATE TABLE IF NOT EXISTS provider_limits (
    scope text PRIMARY KEY,
    state jsonb NOT NULL
);
