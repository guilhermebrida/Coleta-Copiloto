# Descarga GFx
* Arquivo coleta_GFx.py

## Conecta ao banco 
```python
    ENDPOINT="localhost"
    PORT="5432"
    USER="postgres"
    DBNAME="inbox"
    connection = psycopg2.connect(host=ENDPOINT, user=USER, password='postgres', port=PORT, database=DBNAME)
    cursor = connection.cursor() 
```

## Estabelecer conexão com o copiloto 

* Função que estabelece uma conexão serial com um dispositivo em uma porta COM e retorna seu ID.
* Envia QVR para a porta COM utilizando a função generateXVM que deixa o comando no formato em que o
copiloto irá entender
* Argumentos:
    COM (str): A porta COM à qual o dispositivo está conectado.
* Retorna:
    str: O ID do copiloto conectado.

```python
    async def conexao(COM):
        s = serial.Serial(COM, 19200, timeout=10)
        id = '-'
        try:
            for i in range(5):
                xvm = XVM.generateXVM('1234',str(i).zfill(4),'>QVR<')
                print(xvm)
                s.write(xvm.encode())
                resposta = s.readline().decode()
                id = resposta.split(';')[1][3::]
                if id != '1234':
                    print(id)
                    return id
        except Exception:
            print('PORTA SEM COMUNICAÇÃO')
            pass
```

## Comandos de configuração do copiloto
* Função que envia o comando >TCFG53,2< e >VSIP0,TRM1< para ativar a função de descarga do buffer GF0 pela serial
* É necessário utilizar a função generateXVM para formatar os comandos no formato XVM
* Argumentos:
    - COM (str): A porta COM à qual o dispositivo está conectado.
    - device (str): id do copiloto 
* Retorna:
    None


```python
async def configurar(COM,device):
    s = serial.Serial(COM, 19200, timeout=10)
    try:
        for i in range(5):
            xvm = XVM.generateXVM(device,str(i).zfill(4),'>TCFG53,2<')
            print(xvm)
            s.write(xvm.encode())
            resposta = s.readline().decode()
            print(resposta)
            if resposta:
                break
    except Exception as error:
        print('error', error)
    try:
        for i in range(5):
            xvm = XVM.generateXVM(device,str(i).zfill(4),'>VSIP0,TRM1<')
            print(xvm)
            s.write(xvm.encode())
            resposta = s.readline().decode()
            print(resposta)
            if resposta:
                break
    except Exception as error:
        print('error', error)
```


## Coleta das mensagens e Insert no banco 
* Função messages é responsável por enviar um comando >QUV00rTRM< no formato XVM, quando o copiloto receber o comando ele inicia a descarga das mensagens do buffer GF0
* O copiloto só entrega a proxima mensagem se receber o ACK de resposta, ACK é gerado no formato XVM utilizando a função generateAck, que recebe o device_id e a sequence da mensagem 
* A cada mensagem entregue do copiloto essa mensagem é inserida na tabela coleta que contém o device_id, a mensagem entregue e a reception_datetime como colunas

```python
async def messages(COM,device):
    resposta = ''
    s = serial.Serial(COM, 19200,timeout=3)
    xvm = XVM.generateXVM(device,'8000','>QUV00rTRM<')
    s.write(xvm.encode())
    while True:
        resposta = s.readline().decode()
        print(resposta)
        if resposta == '':
            print('acabou')
            break
        else:
            xvmMessage = XVM.parseXVM(resposta)
            msg = xvmMessage[0]
            device_id = xvmMessage[1]
            sequence = xvmMessage[2]
            print('msg:{},  device_id:{},  sequence:{}'.format(msg,device_id,sequence))
            ack = XVM.generateAck(device_id,sequence)
            print(ack)
            s.write(ack.encode())
            cursor.execute('INSERT INTO coleta ("device_id", "message") values (\'{}\', \'{}\');'.format(device_id, resposta))
            connection.commit()
```

### A função message em partes 
* Envia o comando para o copiloto descarregar as mensagens
```python
async def messages(COM,device):
    resposta = ''
    s = serial.Serial(COM, 19200,timeout=3)
    xvm = XVM.generateXVM(device,'8000','>QUV00rTRM<')
    s.write(xvm.encode())
```
* Loop para coletar as mensagens até acabar
```python
    while True:
        resposta = s.readline().decode()
        print(resposta)
        if resposta == '':
            print('acabou')
            break
```
* Faz o parser das mensagens para obter a sequence correta,utilizando a função parserXVM, e em seguida gera o ACK, utilizando a função generateAck 
```python
        else:
            xvmMessage = XVM.parseXVM(resposta)
            msg = xvmMessage[0]
            device_id = xvmMessage[1]
            sequence = xvmMessage[2]
            print('msg:{},  device_id:{},  sequence:{}'.format(msg,device_id,sequence))
            ack = XVM.generateAck(device_id,sequence)
            print(ack)
            s.write(ack.encode())
```
* Faz o insert no banco postgres 
```python
            cursor.execute('INSERT INTO coleta ("device_id", "message") values (\'{}\', \'{}\');'.format(device_id, resposta))
            connection.commit()
```


## Main
* Função Main responsavel por chamar as outras funções, utiliznado os argumentos necessários.
```python
async def main():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        print(p)
        print('estabelecendo conexao...')
        id = await asyncio.create_task(conexao(p.device))
        await asyncio.create_task(configurar(p.device,id))
        await asyncio.create_task(messages(p.device,id))
```

## Botando para rodar
```python
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```



