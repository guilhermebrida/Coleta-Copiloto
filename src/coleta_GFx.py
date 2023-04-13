import serial
import re
import asyncio
from time import sleep
import XVM
import serial.tools.list_ports
import psycopg2

"""
Conecta ao banco postgres
"""

ENDPOINT="localhost"
PORT="5432"
USER="postgres"
DBNAME="inbox"
connection = psycopg2.connect(host=ENDPOINT, user=USER, password='postgres', port=PORT, database=DBNAME)
cursor = connection.cursor()



async def conexao(COM):
    """
    Função que estabelece uma conexão serial com um dispositivo em uma porta COM e retorna seu ID.
    
    Envia QVR para a porta COM utilizando a função generateXVM deixa o comando no formato em que o
    copiloto irá entender

    Argumentos:
        COM (str): A porta COM à qual o dispositivo está conectado.

    Retorna:
        str: O ID do dispositivo conectado.
    """
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
            cursor.execute('INSERT INTO teste ("device_id", "message") values (\'{}\', \'{}\');'.format(device_id, resposta))
            connection.commit()


async def main():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        print(p)
        print('estabelecendo conexao...')
        id = await asyncio.create_task(conexao(p.device))
        await asyncio.create_task(configurar(p.device,id))
        await asyncio.create_task(messages(p.device,id))


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass