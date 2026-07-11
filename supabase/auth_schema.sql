-- Run once in Supabase SQL Editor.
do $$ begin
  create type public.app_role as enum ('admin', 'qa', 'maintenance', 'ops');
exception when duplicate_object then null; end $$;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  role public.app_role not null default 'maintenance',
  approved boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.profiles enable row level security;
grant select on table public.profiles to authenticated;
drop policy if exists "Users can read their profile" on public.profiles;
create policy "Users can read their profile" on public.profiles for select using (auth.uid() = id);
drop policy if exists "Users can update their profile" on public.profiles;

create or replace function public.handle_new_user() returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, full_name, role, approved) values (
    new.id,
    coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
    case when new.raw_user_meta_data->>'requested_role' in ('admin','qa','maintenance','ops')
      then (new.raw_user_meta_data->>'requested_role')::public.app_role else 'maintenance'::public.app_role end,
    true
  ) on conflict (id) do nothing;
  return new;
end; $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute procedure public.handle_new_user();

-- Optional but recommended: enable this function under Authentication > Hooks >
-- Custom Access Token so newly issued JWTs contain a trusted `user_role` claim.
create or replace function public.custom_access_token_hook(event jsonb)
returns jsonb language plpgsql stable as $$
declare claims jsonb; assigned_role public.app_role;
begin
  select role into assigned_role from public.profiles where id = (event->>'user_id')::uuid;
  claims := event->'claims';
  if assigned_role is not null then claims := jsonb_set(claims, '{user_role}', to_jsonb(assigned_role)); end if;
  return jsonb_set(event, '{claims}', claims);
end; $$;
grant usage on schema public to supabase_auth_admin;
grant execute on function public.custom_access_token_hook(jsonb) to supabase_auth_admin;
revoke execute on function public.custom_access_token_hook(jsonb) from authenticated, anon, public;
grant select on table public.profiles to supabase_auth_admin;
drop policy if exists "Auth hook can read roles" on public.profiles;
create policy "Auth hook can read roles" on public.profiles for select to supabase_auth_admin using (true);
