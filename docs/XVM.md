# XVM
## calcCheckSum
* Função responsável para calcular o checksum de cada mensagem no padrão XVM
* Recebe: mensagem(str)
```python
def calcCheckSum (msg):
    num = msg.find(';*')+1
    calc = 0
    for i in range(num): calc ^= ord(msg[i])
    return calc
```
## parseXVM
* Função responsável por separar todos os atributos contidos em uma mensagem XVM
* Recebe: mensagem(str)
```python
def parseXVM(msg):
    xvmMessage=msg.split(';')  
    message  = xvmMessage[0]
    id       = xvmMessage[1][3:]
    sequence = int(xvmMessage[2][1:],16)
    checksum = int(xvmMessage[3][1:3],16)
    return (message,id,sequence,checksum) 
```
## generateAck
* Função que gera o ACK do copiloto
* Recebe: id (str) e sequence (str)
```python
def generateAck(id,sequence):
    resp = '>ACK;ID='+id+';#'+format(sequence,'04X')+';*'
    resp = resp+format(calcCheckSum(resp),'02X')+'<\r\n'
    return resp
```
## generateXVM
* Função que gera uma mensagem XVM
* Recebe: id (str), sequence (str), message (str)
```python
def generateXVM(id,sequence,message):
    resp = message+';ID='+id+';#'+sequence+';*'
    resp = resp+format(calcCheckSum(resp),'02X')+'<\r\n'
    return resp
```
## isValidXVM
* Função valida se a mensagem recebida é uma mensagem no padrão XVM
* Recebe: id (str), sequence (str), message (str)
```python
def isValidXVM(msg):
    return 1 if calcCheckSum(msg)==parseXVM(msg)[3] else 0
```