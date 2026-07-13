-- IA/360 Avanzado — almacenamiento seguro del progreso
-- Ejecutar una sola vez en Supabase. El script es idempotente y puede repetirse.
-- En el navegador sólo se utiliza la Project URL y la Publishable key.
-- Nunca publique una secret key ni service_role.

create table if not exists public.ai_study_progress (
  user_id uuid primary key references auth.users(id) on delete cascade,
  state jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.ai_study_progress enable row level security;

revoke all on table public.ai_study_progress from anon;
grant select, insert, update, delete on table public.ai_study_progress to authenticated;

drop policy if exists "read own study progress" on public.ai_study_progress;
drop policy if exists "insert own study progress" on public.ai_study_progress;
drop policy if exists "update own study progress" on public.ai_study_progress;
drop policy if exists "delete own study progress" on public.ai_study_progress;

create policy "read own study progress"
on public.ai_study_progress
for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "insert own study progress"
on public.ai_study_progress
for insert
to authenticated
with check ((select auth.uid()) = user_id);

create policy "update own study progress"
on public.ai_study_progress
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create policy "delete own study progress"
on public.ai_study_progress
for delete
to authenticated
using ((select auth.uid()) = user_id);

comment on table public.ai_study_progress is
  'Estado sincronizado de IA/360. Cada usuario sólo puede acceder a su propia fila mediante RLS.';
