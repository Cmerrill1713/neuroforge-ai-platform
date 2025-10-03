-- Simple Vector Store Database Setup (without pgvector)
-- Run this script to initialize the vector database

-- Use the ai_system database
\c ai_system;

-- Create vector_documents table for storing document embeddings (without vector column)
CREATE TABLE IF NOT EXISTS vector_documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    embedding_json JSONB, -- Store embeddings as JSON arrays
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for metadata queries
CREATE INDEX IF NOT EXISTS idx_vector_documents_metadata
ON vector_documents USING GIN (metadata);

-- Create knowledge_base table for structured knowledge
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    tags TEXT[],
    embedding_json JSONB, -- Store embeddings as JSON arrays
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for category and tags
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category
ON knowledge_base (category);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_tags
ON knowledge_base USING GIN (tags);

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Create sessions table for session management
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_token
ON user_sessions (session_token);

CREATE INDEX IF NOT EXISTS idx_user_sessions_expires
ON user_sessions (expires_at);

-- Insert default admin user
INSERT INTO users (username, email, password_hash, role)
VALUES (
    'admin',
    'admin@localhost',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj', -- Admin123!@#
    'admin'
)
ON CONFLICT (username) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_vector_documents_updated_at
    BEFORE UPDATE ON vector_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at
    BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_user;

-- Verify setup
SELECT 'Simple vector store database setup complete!' as status;
