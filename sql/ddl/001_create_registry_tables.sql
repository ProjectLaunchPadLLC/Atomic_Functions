-- 001_create_registry_tables.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Libraries table
CREATE TABLE IF NOT EXISTS libraries (
  id TEXT PRIMARY KEY,
  display_name TEXT,
  alias TEXT,
  description TEXT,
  owner_id UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_libraries_alias ON libraries(alias);

-- Contributors table
CREATE TABLE IF NOT EXISTS contributors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username TEXT UNIQUE,
  display_name TEXT,
  email TEXT,
  profile JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Functions table (core registry)
CREATE TABLE IF NOT EXISTS functions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  display_name TEXT,
  module_path TEXT NOT NULL,
  category TEXT NOT NULL,
  subcategories TEXT[],
  signature JSONB NOT NULL,
  description TEXT NOT NULL,
  examples TEXT[],
  tags TEXT[],
  source TEXT NOT NULL,
  contributor_id UUID REFERENCES contributors(id),
  license TEXT NOT NULL,
  visibility TEXT NOT NULL CHECK (visibility IN ('public','org','private')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  version TEXT NOT NULL,
  usage_count BIGINT NOT NULL DEFAULT 0,
  last_used_at TIMESTAMP WITH TIME ZONE,
  payout_config JSONB,
  ai_metadata JSONB,
  integrity_hash TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_functions_name ON functions(name);
CREATE INDEX IF NOT EXISTS idx_functions_category ON functions(category);
CREATE INDEX IF NOT EXISTS idx_functions_source ON functions(source);
CREATE INDEX IF NOT EXISTS idx_functions_usage_count ON functions(usage_count DESC);

-- Usage events (append-only, batched ingestion)
CREATE TABLE IF NOT EXISTS usage_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  function_id UUID NOT NULL REFERENCES functions(id),
  event_type TEXT NOT NULL,
  occurred_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_usage_events_function ON usage_events(function_id);
CREATE INDEX IF NOT EXISTS idx_usage_events_time ON usage_events(occurred_at);

-- Audit log for registry changes (append-only)
CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  action TEXT NOT NULL,
  performed_by UUID,
  performed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  diff JSONB
);

CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);

-- Optional: materialized view for fast search (text search)
CREATE MATERIALIZED VIEW IF NOT EXISTS functions_search AS
SELECT
  id,
  name,
  display_name,
  description,
  array_to_string(tags, ' ') AS tags_text,
  category,
  source,
  to_tsvector('english', coalesce(display_name,'') || ' ' || coalesce(description,'') || ' ' || coalesce(array_to_string(tags,' '),'')) AS document
FROM functions;

CREATE INDEX IF NOT EXISTS idx_functions_search_document ON functions_search USING GIN(document);

-- Trigger to refresh materialized view on changes (simple approach for MVP)
CREATE OR REPLACE FUNCTION refresh_functions_search() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  PERFORM pg_sleep(0); -- placeholder to allow async refresh strategies
  RETURN NEW;
END;
$$;

-- Note: For production, use an async job to refresh the materialized view or use a dedicated search engine.

