# Banco de Dados

## init.db
* Exemplo de tabela para a inserção dos dados, 
* Colunas:
    - device_id: o id do copiloto
    - message: a mensagem coletada pela serial
    - reception_datetime: data e hora da coleta da mensagem, timezone de São Paulo
```sql
CREATE TABLE IF NOT EXISTS public.coleta
(
    device_id text COLLATE pg_catalog."default" NOT NULL,
    message text COLLATE pg_catalog."default",
    reception_datetime timestamp with time zone DEFAULT timezone('America/Sao_Paulo', now())
);
```