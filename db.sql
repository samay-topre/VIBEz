-- 1. AI Vector Support
create extension if not exists vector;

-- 2. Users Table

-- [Keep all previous SQL tables, but ensure 'featured_vibes' exists]
create table if not exists featured_vibes (
  id uuid primary key default gen_random_uuid(),
  content text not null,
  category text not null
);

create table app_users (
  id uuid primary key default gen_random_uuid(),
  user_id_alias text unique not null, 
  email text not null,
  password text not null,
  age int not null check (age >= 18),
  device_hash text not null,
  created_at timestamp with time zone default now()
);

-- 3. Vibes Table
create table reviews (
  id bigserial primary key,
  author_id uuid references app_users(id),
  category text not null,
  content text not null,
  embedding vector(384),
  upvotes int default 0,
  downvotes int default 0,
  created_at timestamp with time zone default now()
);

-- 4. Stream Table
create table featured_vibes (
  id uuid primary key default gen_random_uuid(),
  content text not null,
  category text not null
);

-- 5. AI Search Function
create or replace function match_reviews (
  query_embedding vector(384),
  match_count int,
  search_category text
)
returns table (
  id bigint,
  user_alias text,
  content text,
  similarity float,
  upvotes int,
  downvotes int,
  category text
)
language plpgsql
as $$
begin
  return query
  select
    reviews.id,
    app_users.user_id_alias as user_alias,
    reviews.content,
    (1 - (reviews.embedding <=> query_embedding)) * 100 as similarity,
    reviews.upvotes,
    reviews.downvotes,
    reviews.category
  from reviews
  join app_users on reviews.author_id = app_users.id
  order by (case when reviews.category = search_category then 1 else 0 end) desc, 
           reviews.embedding <=> query_embedding
  limit match_count;
end;
$$;