DO $$ BEGIN
  CREATE ROLE anon NOLOGIN; CREATE ROLE authenticated NOLOGIN; CREATE ROLE service_role NOLOGIN;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
CREATE TABLE public.user_profiles (
  user_id UUID PRIMARY KEY, birth_data JSONB, chart JSONB, dashas JSONB, validation JSONB,
  goals JSONB, habits JSONB, chat_history JSONB, coaching JSONB, updated_at TIMESTAMPTZ
);
CREATE TABLE public.coaching_observations (
  id BIGSERIAL PRIMARY KEY, user_id UUID NOT NULL, observation_id TEXT, "timestamp" TIMESTAMPTZ,
  text TEXT, category TEXT, exchange_index INTEGER
);
