-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

--------------------------------------------------
-- USERS
--------------------------------------------------

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_id BIGINT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    email TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

--------------------------------------------------
-- REPOSITORIES
--------------------------------------------------

CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,
    github_url TEXT UNIQUE NOT NULL,
    default_branch TEXT DEFAULT 'main',
    language TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_analyzed TIMESTAMPTZ
);

--------------------------------------------------
-- COMMITS
--------------------------------------------------

CREATE TABLE commits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    commit_sha TEXT UNIQUE NOT NULL,
    author TEXT,
    message TEXT,
    commit_date TIMESTAMPTZ
);

--------------------------------------------------
-- FILES
--------------------------------------------------

CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    language TEXT,
    size BIGINT,
    content TEXT,
    embedding VECTOR(1536)
);

--------------------------------------------------
-- ANALYSES
--------------------------------------------------

CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending',
    summary TEXT,
    risk_score INTEGER,
    technical_debt TEXT,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

--------------------------------------------------
-- CHAT HISTORY
--------------------------------------------------

CREATE TABLE chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

--------------------------------------------------
-- INDEXES
--------------------------------------------------

CREATE INDEX idx_repositories_user ON repositories(user_id);
CREATE INDEX idx_commits_repo ON commits(repository_id);
CREATE INDEX idx_files_repo ON files(repository_id);
CREATE INDEX idx_analyses_repo ON analyses(repository_id);
CREATE INDEX idx_chat_repo ON chat_history(repository_id);
