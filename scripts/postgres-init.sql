-- ============================================================================
-- NeuroForge PostgreSQL Initialization Script - Phase 5
-- Database schema and initial data setup for production
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_buffercache";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- API Keys and Authentication
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    rate_limit INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255)
);

-- User Sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    session_token VARCHAR(512) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- EXPERIMENTATION & ANALYTICS TABLES
-- ============================================================================

-- Experiment Metadata
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL, -- 'prompt_optimization', 'model_comparison', etc.
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'failed'
    config JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Experiment Results
CREATE TABLE IF NOT EXISTS experiment_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    model_name VARCHAR(255) NOT NULL,
    prompt_text TEXT NOT NULL,
    response_text TEXT,
    metrics JSONB DEFAULT '{}',
    quality_score DECIMAL(3,2),
    latency_ms INTEGER,
    tokens_used INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- MONITORING & LOGGING TABLES
-- ============================================================================

-- System Metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(15,6),
    metric_type VARCHAR(50), -- 'counter', 'gauge', 'histogram'
    labels JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API Request Logs
CREATE TABLE IF NOT EXISTS api_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(255) UNIQUE,
    method VARCHAR(10) NOT NULL,
    path TEXT NOT NULL,
    query_params JSONB DEFAULT '{}',
    headers JSONB DEFAULT '{}',
    request_body TEXT,
    response_status INTEGER,
    response_body TEXT,
    response_time_ms INTEGER,
    ip_address INET,
    user_agent TEXT,
    api_key_id UUID REFERENCES api_keys(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Error Logs
CREATE TABLE IF NOT EXISTS error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    context JSONB DEFAULT '{}',
    severity VARCHAR(20) DEFAULT 'error', -- 'debug', 'info', 'warning', 'error', 'critical'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(255)
);

-- ============================================================================
-- CACHE & PERFORMANCE TABLES
-- ============================================================================

-- Cache Metadata
CREATE TABLE IF NOT EXISTS cache_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(512) UNIQUE NOT NULL,
    cache_type VARCHAR(50) NOT NULL, -- 'prompt', 'embedding', 'result'
    size_bytes INTEGER,
    hits INTEGER DEFAULT 0,
    misses INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Performance Metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operation_type VARCHAR(100) NOT NULL,
    operation_name VARCHAR(255) NOT NULL,
    duration_ms INTEGER NOT NULL,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- VECTOR DATABASE METADATA
-- ============================================================================

-- Vector Collections
CREATE TABLE IF NOT EXISTS vector_collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    vector_dimension INTEGER NOT NULL,
    distance_metric VARCHAR(50) DEFAULT 'cosine',
    index_type VARCHAR(50) DEFAULT 'hnsw',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Embedding Metadata
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_id UUID NOT NULL REFERENCES vector_collections(id) ON DELETE CASCADE,
    content_hash VARCHAR(128) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    embedding_vector VECTOR(768), -- Adjust dimension based on model
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- API Keys
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);

-- User Sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

-- Experiments
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_experiments_type ON experiments(type);
CREATE INDEX IF NOT EXISTS idx_experiments_created ON experiments(created_at DESC);

-- Experiment Results
CREATE INDEX IF NOT EXISTS idx_experiment_results_experiment ON experiment_results(experiment_id);
CREATE INDEX IF NOT EXISTS idx_experiment_results_model ON experiment_results(model_name);
CREATE INDEX IF NOT EXISTS idx_experiment_results_quality ON experiment_results(quality_score);

-- System Metrics
CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

-- API Requests
CREATE INDEX IF NOT EXISTS idx_api_requests_timestamp ON api_requests(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_requests_status ON api_requests(response_status);
CREATE INDEX IF NOT EXISTS idx_api_requests_path ON api_requests(path);
CREATE INDEX IF NOT EXISTS idx_api_requests_api_key ON api_requests(api_key_id);

-- Error Logs
CREATE INDEX IF NOT EXISTS idx_error_logs_type ON error_logs(error_type);
CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON error_logs(severity);
CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_logs_resolved ON error_logs(resolved);

-- Cache Metadata
CREATE INDEX IF NOT EXISTS idx_cache_metadata_key ON cache_metadata(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_metadata_type ON cache_metadata(cache_type);
CREATE INDEX IF NOT EXISTS idx_cache_metadata_expires ON cache_metadata(expires_at);

-- Performance Metrics
CREATE INDEX IF NOT EXISTS idx_performance_metrics_operation ON performance_metrics(operation_type, operation_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp DESC);

-- Vector Collections
CREATE INDEX IF NOT EXISTS idx_vector_collections_name ON vector_collections(name);

-- Embeddings
CREATE INDEX IF NOT EXISTS idx_embeddings_collection ON embeddings(collection_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_hash ON embeddings(content_hash);

-- ============================================================================
-- DEFAULT DATA
-- ============================================================================

-- Insert default API key for development
INSERT INTO api_keys (key_hash, name, description, permissions, rate_limit, created_by)
VALUES (
    encode(sha256('neuroforge-dev-key'::bytea), 'hex'),
    'Development API Key',
    'Default API key for development and testing',
    '{"read": true, "write": true, "admin": true}',
    10000,
    'system'
) ON CONFLICT (key_hash) DO NOTHING;

-- Insert default vector collection
INSERT INTO vector_collections (name, description, vector_dimension, distance_metric)
VALUES (
    'neuroforge-knowledge',
    'Main knowledge base for NeuroForge embeddings',
    768,
    'cosine'
) ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- API Usage Summary View
CREATE OR REPLACE VIEW api_usage_summary AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN response_status >= 200 AND response_status < 300 THEN 1 END) as success_requests,
    COUNT(CASE WHEN response_status >= 400 THEN 1 END) as error_requests,
    AVG(response_time_ms) as avg_response_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time
FROM api_requests
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

-- Experiment Performance View
CREATE OR REPLACE VIEW experiment_performance AS
SELECT
    e.id,
    e.name,
    e.type,
    e.status,
    COUNT(er.id) as total_results,
    AVG(er.quality_score) as avg_quality_score,
    AVG(er.latency_ms) as avg_latency_ms,
    AVG(er.tokens_used) as avg_tokens_used,
    MIN(er.created_at) as first_result_at,
    MAX(er.created_at) as last_result_at
FROM experiments e
LEFT JOIN experiment_results er ON e.id = er.experiment_id
GROUP BY e.id, e.name, e.type, e.status;

-- System Health View
CREATE OR REPLACE VIEW system_health AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    metric_name,
    AVG(metric_value) as avg_value,
    MIN(metric_value) as min_value,
    MAX(metric_value) as max_value,
    COUNT(*) as sample_count
FROM system_metrics
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp), metric_name
ORDER BY hour DESC, metric_name;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to clean old data (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INTEGER DEFAULT 90)
RETURNS TABLE(deleted_records BIGINT) AS $$
DECLARE
    deleted_count BIGINT;
BEGIN
    -- Clean old API requests
    DELETE FROM api_requests WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN QUERY SELECT deleted_count;

    -- Clean old performance metrics
    DELETE FROM performance_metrics WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN QUERY SELECT deleted_count;

    -- Clean expired sessions
    DELETE FROM user_sessions WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN QUERY SELECT deleted_count;

    -- Clean old system metrics
    DELETE FROM system_metrics WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN QUERY SELECT deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get API key by hash
CREATE OR REPLACE FUNCTION get_api_key(key_hash_input VARCHAR)
RETURNS TABLE (
    id UUID,
    name VARCHAR,
    permissions JSONB,
    rate_limit INTEGER,
    is_active BOOLEAN,
    expires_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT ak.id, ak.name, ak.permissions, ak.rate_limit, ak.is_active, ak.expires_at
    FROM api_keys ak
    WHERE ak.key_hash = key_hash_input
    AND ak.is_active = true
    AND (ak.expires_at IS NULL OR ak.expires_at > NOW());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update last_used_at for API keys
CREATE OR REPLACE FUNCTION update_api_key_last_used()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE api_keys SET last_used_at = NOW() WHERE id = NEW.api_key_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER api_request_update_key_usage
    AFTER INSERT ON api_requests
    FOR EACH ROW
    WHEN (NEW.api_key_id IS NOT NULL)
    EXECUTE FUNCTION update_api_key_last_used();

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

-- Grant permissions for the neuroforge user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO neuroforge;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO neuroforge;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO neuroforge;

-- Grant read access to views
GRANT SELECT ON api_usage_summary TO neuroforge;
GRANT SELECT ON experiment_performance TO neuroforge;
GRANT SELECT ON system_health TO neuroforge;
