-- ============================================================================
-- GitHub Time Machine — Schema v2: functions + edges (Knowledge Graph)
-- Run in Supabase SQL Editor AFTER the base schema is in place
-- ============================================================================

-- 1. Tables
-- ---------------------------------------------------------------------------

create table if not exists functions (
    id uuid primary key default gen_random_uuid(),
    file_id uuid not null references files(id) on delete cascade,
    repository_id uuid not null references repositories(id) on delete cascade,
    name text not null,
    signature text,
    start_line integer not null,
    end_line integer not null,
    is_exported boolean default false,
    created_at timestamptz default now()
);

create table if not exists edges (
    id uuid primary key default gen_random_uuid(),
    repository_id uuid not null references repositories(id) on delete cascade,
    source_id uuid not null,
    target_id uuid not null,
    edge_type text not null
        check (edge_type in ('calls', 'imports', 'extends', 'implements', 'depends_on')),
    source_name text,
    target_name text,
    metadata jsonb default '{}'::jsonb,
    created_at timestamptz default now()
);


-- 2. Indexes
-- ---------------------------------------------------------------------------

create index if not exists idx_functions_repo on functions(repository_id);
create index if not exists idx_functions_file on functions(file_id);
create index if not exists idx_edges_repo on edges(repository_id);
create index if not exists idx_edges_source on edges(source_id);
create index if not exists idx_edges_target on edges(target_id);
create index if not exists idx_edges_type on edges(edge_type);


-- 3. Row Level Security
-- ---------------------------------------------------------------------------

alter table functions force row level security;
alter table edges force row level security;

create policy "functions_select_own" on functions
    for select using (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );
create policy "functions_insert_own" on functions
    for insert with check (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );

create policy "edges_select_own" on edges
    for select using (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );
create policy "edges_insert_own" on edges
    for insert with check (
        exists (select 1 from repositories r
                where r.id = repository_id and r.user_id = auth.uid())
    );
