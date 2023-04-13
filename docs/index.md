# Coleta GFx Copiloto
***Documentação para utilização do codigo em python para coleta das mensagens do buffer GF0 pela serial do copiloto***


## Instalar as dependências
    pip install -r requirements.txt

## Bibliotecas
* `import serial`  - Comunicação serial
* `import asyncio` - Biblioteca assíncrona
* `import XVM`  - Biblioteca para formatação do XVM (linguagem do copiloto)
* `import serial.tools.list_ports` - Listar as portas COM disponíveis
* `import psycopg2` - Biblioteca para se conectar no banco postgres