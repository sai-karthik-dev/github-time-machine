-- ============================================================================
-- GitHub Time Machine — PostgreSQL Schema
-- Run in Supabase SQL Editor
-- ============================================================================

-- 1. Extensions
-- ---------------------------------------------------------------------------

create extension if not exists pgcrypto with schema extensions;
create extension if not exists vector with schema extensions;


-- 2. Tables
-- ---------------------------------------------------------------------------

create table if not exists users (
    id uuid primary key references auth.users on delete cascade,
    github_id bigint unique not null,
    username text not null,
    email text,
    avatar_url text,
    created_at timestamptz default now()
);

create table if not exists repositories (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    name text not null,
    owner text not null,
    github_url text unique not null
        check (github_url ~ '^https?://github\.com/[^/]+/[^/]+'),
    default_branch text default 'main',
    language text,
    created_at timestamptz default now(),
    last_analyzed timestamptz
);

create table if not exists commits (
    id uuid primary key default gen_random_uuid(),
    repository_id uuid not null references repositories(id) on delete cascade,
    commit_sha text unique not null
        check (commit_sha ~ '^[a-f0-9]{40}$'),
    author text,
    message text,
    commit_date timestamptz
);

create table if not exists files (
    id uuid primary key default gen_random_uuid(),
    repository_id uuid not null references repositories(id) on delete cascade,
    file_path text not null,
    language text,
    size bigint default 0
        check (size >= 0),
    content text,
    embedding vector(1536)
);

create table if not exists analyses (
    id uuid primary key default gen_random_uuid(),
    repository_id uuid not null references repositories(id) on delete cascade,
    status text not null default 'pending'
        check (status in ('pending', 'processing', 'completed', 'error')),
    summary text,
    risk_score integer
        check (risk_score >= 0 and risk_score <= 100),
    technical_debt text,
    error_message text,
    started_at timestamptz,
    completed_at timestamptz,
    created_at timestamptz default now()
);


create table if not exists chat_history (
    id uuid primary key default gen_random_uuid(),
    repository_id uuid not null references repositories(id) on delete cascade,
    question text not null,
    answer text,
    created_at timestamptz default now()
);


-- 3. Indexes
-- ---------------------------------------------------------------------------

create index if not exists idx_users_github_id on users(github_id);
create index if not exists idx_repositories_user on repositories(user_id);
create index if not exists idx_repositories_created on repositories(created_at desc);
create index if not exists idx_commits_repo on commits(repository_id);
create index if not exists idx_commits_sha on commits(commit_sha);
create index if not exists idx_files_repo on files(repository_id);
create index if not exists idx_analyses_repo on analyses(repository_id);
create index if not exists idx_chat_repo on chat_history(repository_id);

-- IVF Flat vector index — requires >= 1000 rows. Postgres skips silently if table is near-empty.
create index if not exists idx_files_embedding_ivfflat
    on files
    using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);


-- 4. updated_at trigger on repositories
-- ---------------------------------------------------------------------------

create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.last_analyzed = now();
    return new;
end;
$$ language plpgsql security definer set search_path = '';

drop trigger if exists set_updated_at on repositories;
create trigger set_updated_at
    before update on repositories
    for each row
    execute function public.handle_updated_at();


-- 5. Row Level Security
-- ---------------------------------------------------------------------------

alter table users force row level security;
alter table repositories force row level security;
alter table commits force row level security;
alter table files force row level security;
alter table analyses force row level security;
alter table chat_history force row level security;

-- users: only the owning user can see or modify their own profile
create policy "users_read_own" on users
    for select using (auth.uid() = id);
create policy "users_update_own" on users
    for update using (auth.uid() = id);
create policy "users_insert_own" on users
    for insert with check (auth.uid() = id);

-- repositories: owner has full CRUD
create policy "repos_select_own" on repositories
    for select using (auth.uid() = user_id);
create policy "repos_insert_own" on repositories
    for insert with check (auth.uid() = user_id);
create policy "repos_update_own" on repositories
    for update using (auth.uid() = user_id);
create policy "repos_delete_own" on repositories
    for delete using (auth.uid() = user_id);

-- commits: visible only if the repo belongs to the user
create policy "commits_select_own" on commits
    for select using (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );
create policy "commits_insert_own" on commits
    for insert with check (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );

-- files: visible only if the repo belongs to the user
create policy "files_select_own" on files
    for select using (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );
create policy "files_insert_own" on files
    for insert with check (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );

-- analyses: visible only if the repo belongs to the user
create policy "analyses_select_own" on analyses
    for select using (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );
create policy "analyses_insert_own" on analyses
    for insert with check (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );

-- chat_history: visible only if the repo belongs to the user
create policy "chat_select_own" on chat_history
    for select using (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );
create policy "chat_insert_own" on chat_history
    for insert with check (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );
