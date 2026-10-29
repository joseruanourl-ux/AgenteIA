-- Ejecuta esto UNA vez en Supabase: SQL Editor -> New query -> pegar -> Run

create table if not exists public.conversaciones (
  owner      text        not null,   -- hash de usuario + PIN (nunca el PIN en texto)
  id         text        not null,   -- id de la conversación
  title      text        not null default 'Nueva conversación',
  created    text,
  updated    text,
  chat       jsonb       not null default '[]'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (owner, id)
);

-- Seguridad: con RLS activado y SIN políticas, la clave pública (publishable) no puede
-- leer ni escribir nada. Solo tu app, con la clave secret guardada en Secrets, tiene acceso.
alter table public.conversaciones enable row level security;
