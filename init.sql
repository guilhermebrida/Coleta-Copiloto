CREATE TABLE IF NOT EXISTS public.coleta
(
    device_id text COLLATE pg_catalog."default" NOT NULL,
    message text COLLATE pg_catalog."default",
    reception_datetime timestamp with time zone DEFAULT timezone('America/Sao_Paulo', now())
);
