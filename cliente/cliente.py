import socket
import json
import os
import time
HOST = '172.16.103.238' #IP (tem que ser trocado para o ip do computador em que o controller está)
PORT = 3003 #Número da porta
HOST_RFID = '172.16.103.0'
PORT_RFID = 7890 #porta para o rfid
envio_controller = {}
#Insere os produtos manualmente (TAGS)
def inserir_prod(servidor):
    
    produto = input("Digite o TAG do produto: ")
    envio_controller = {'header':'id', 'body': produto}
    print('AGUARDE!!! PROCESSANDO INFORMAÇÕES...')
    servidor.send(json.dumps(envio_controller).encode()) #Enviando uma mensagem para o servidor e codificando ela como uma string
    resposta = servidor.recv(1024).decode('utf-8') #Recebe os dados ecoados pelo servidor
    if resposta == 'BLOCK':
        print('CAIXA BLOQUEADO')
        time.sleep(5)
        return
#lê as tags pelo RFID
def ler_tags(servidor):
    while True:
        servidor_rfid = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #objeto socket IPV4 e TCP
        servidor_rfid.connect((HOST_RFID, PORT_RFID)) #Pedindo para conectar com o servidor
        tags = servidor_rfid.recv(1024).decode('utf-8')
        
        lista = json.loads(tags)
        print('AGUARDE!!! PROCESSANDO INFORMAÇÕES...')
        for i in  lista:
            envio_controller = {'header':'id', 'body': i}
            servidor.send(json.dumps(envio_controller).encode())
            resposta = servidor.recv(1024).decode('utf-8')
            if resposta == 'BLOCK':
                print('CAIXA BLOQUEADO')
                time.sleep(5)
                return
        break
#Finaliza a compra
def finalizar_compra(servidor):
    envio_controller = {'header':'compra'}
    resposta = servidor.send(json.dumps(envio_controller).encode())
    resposta = servidor.recv(1024).decode('utf-8')
    if resposta == 'carrinho_vazio':
        print('O Carrinho de compras está vazio!!!')
        time.sleep(5)
    
    elif resposta == 'BLOCK':
        print('CAIXA BLOQUEADO')
        time.sleep(5)
        return
    
    else:
        print('COMPRA FINALIZADA COM SUCESSO! TENHA UM BOM DIA!!!')
        time.sleep(5)
#Visualiza o carrinho atual
def visualizar_carrinho(servidor):
    envio_controller = {'header':'visualizar_carrinho'}
    servidor.send(json.dumps(envio_controller).encode())
    resposta = servidor.recv(1024).decode('utf-8')
    if resposta == 'carrinho_vazio':
        print('O Carrinho de compras está vazio!!!')
        time.sleep(5)
    elif resposta == 'BLOCK':
        print('CAIXA BLOQUEADO')
        time.sleep(5)
        return
        
    else:
        resposta = json.loads(resposta)
        valor_total = 0
        os.system('cls')
        for i in resposta:
            print('PRODUTO: ',resposta[i]['Nome'], '|' ,'QUANTIDADE: ', resposta[i]['Quant'], '|' ,'VALOR: ', resposta[i]['Val'])
            valor_total += resposta[i]['Val']
        print('VALOR TOTAL: ', valor_total)
        i = input('Digite qualquer coisa para voltar para o menu!!!')
#Menu principal
def menu():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #objeto socket IPV4 e TCP
    servidor.connect((HOST, PORT)) #Pedindo para conectar com o servidor
    while True:
        
        os.system('cls')
        print('===============================================')
        print('Menu')
        print('===============================================')
        print('[1] Ler produtos')
        print('[2] Finalizar compra')
        print('[3] Ver carrinho')
        print('[4] Inserir produto manualmente')
        
        opcao = input('')
        if opcao == '1':
            ler_tags(servidor)
        elif opcao == '2':
            finalizar_compra(servidor)
        elif opcao == '3':
            visualizar_carrinho(servidor)
        elif opcao == '4':
            inserir_prod(servidor)
        else:
            print('Opção invalida... Insira um digito correspondente a alugma das opções presentes no menu!!!')

if __name__ == "__main__": 
    menu()

#print("Mensagem retornada: ", data.decode()) #Mostrando a mensagem retornada e decodificando como mensagem
