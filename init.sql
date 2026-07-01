CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

CREATE TABLE IF NOT EXISTS domains (
    id BIGSERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    creation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_domain_btree ON domains(domain);
CREATE INDEX IF NOT EXISTS idx_domain_trgm ON domains USING gin (domain gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_creation_date ON domains(creation_date);
ALTER TABLE domains SET (autovacuum_enabled = false);
