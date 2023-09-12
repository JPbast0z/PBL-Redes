import json
import requests
import threading
import socket

HOST = '10.65.131.39' #IP
PORT = 3003 #Número da porta
acesso_caixa = {}


#Cria uma threads para cada conexão/caixa
def create_thread(servidor):
    while True:
        conn, ender = servidor.accept() #retorno da conexão, conexão e endereço
        client_thread = threading.Thread(target=acesso_cliente, args=(conn, ender,))
        client_thread.start()
        print("conectado em:", ender) #mensagem informando que a conexão foi aceita
        print("---CONEXÕES ATIVAS: ", threading.active_count() - 1)
#Faz a requisição que verifica o acesso dos caixas
def verificar_caixa(client_port):
    url_verifica = 'http://localhost:3003/' + 'verifica_caixa'
    finaliza = {'caixa' : client_port}
    response = requests.post(url_verifica,json=finaliza)
    if response.status_code == 200: 
        return True
    else:
        return False 
#Faz a requisição que altera o acesso dos caixas
def acesso_caixa(client_port):
    finaliza = {'caixa' : client_port}
    url = 'http://localhost:3003/' + 'acesso_caixa'
    response = requests.post(url, json=finaliza)

def acesso_cliente(conn, ender):
    #Pega a porta e o ip de cada caixa
    client_ip, client_port = conn.getpeername()
    try:
        while True:
            #Recebe o pedido do caixa
            pedido = conn.recv(1024).decode('utf-8')
            pedido = json.loads(pedido)
            #Verifica a se o caixa atual tem acesso liberado
            autorizar = verificar_caixa(client_port)
            
            #Caso o caixa esteja bloqueado ele não tem acesso a nenhuma requisição
            if autorizar == False:
                mensagem = 'BLOCK'
                conn.send(mensagem.encode('utf-8'))
            
            #Adiciona item ao carrinho
            elif pedido['header'] == 'id':
                
                url = 'http://localhost:3003/' + 'id/'+ pedido['body']
                requisicao = requests.get(url)
                if requisicao.status_code == 200:  
                    conteudo = requisicao.json()  
                    url_carrinho = 'http://localhost:3003/' + 'carrinho'
                    dict_carrinho = {'port' : client_port, 'tag' : pedido['body'] ,'pedido' : conteudo} 
                    response = requests.post(url_carrinho, json=dict_carrinho)
                    conn.send(json.dumps(conteudo).encode('utf-8'))
                    
                elif requisicao.status_code == 204:
                    conteudo = requisicao.text
                    conn.send('222'.encode('utf-8'))
            #Finaliza a compra
            elif pedido['header'] == 'compra':
                finaliza = {'caixa' : client_port}
                url = 'http://localhost:3003/' + 'compra/' #alterar
                response = requests.post(url,json=finaliza)
                if response.status_code == 200:  
                    conn.send('Compra_realizada'.encode('utf-8'))
                else:
                    conn.send('A compra não pode ser finalizada, um ou mais itens não estão contidos ou não tem quantidade suficiente no estoque!!! Seu carrinho foi limpo...'.encode('utf-8'))
            #Chama a função que altera o acesso dos caixas  
            elif pedido['header'] == 'acesso_caixa':
                acesso_caixa(client_port)
            #Faz a requisição que retorna o carrinho de compras
            elif pedido['header'] == 'visualizar_carrinho':
                url = 'http://localhost:3003/' + 'visualizar_carrinho/' + str(client_port)
                response = requests.get(url)
                if response.status_code == 200:
                    conteudo = response.json()
                    conn.send(json.dumps(conteudo).encode('utf-8'))
                else:
                    conn.send('carrinho_vazio'.encode('utf-8'))
            
            else:
                print(f"A requisição falhou com código de status {requisicao.status_code}")
               
            if not pedido:
                break  # Cliente fechou a conexão
            
            print("Pedido:", pedido)
            #resposta = 'enviooou'
            #conn.send(resposta.encode('utf-8'))
        
    except Exception as e:
        print("Ocorreu um erro:", e)
        
    print("Conexão fechada:", ender)
#parte do programa que abre a conexão socket e cria uma thread que instancia outras threads individuais para aceitar conexões com diferentes caixas
def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #objeto socket IPV6 e TCP
    servidor.bind((HOST, PORT)) #vinculando o socket (servidor e a porta)
    servidor.listen() #Entrando no modo de escuta
    new_thread = threading.Thread(target=create_thread, args=(servidor,))
    new_thread.start()

print("Aguardando conexão")

if __name__ == "__main__": 
    main()
