from dadosServer import dados
from http.server import BaseHTTPRequestHandler, HTTPServer
import json



HOST = '172.20.10.3' #ip
HOST_SERVER = 'http://localhost:3003/'

carrinho_compras = {}
historico_geral_compras = {}
caixas = {}


#Classe que manipula solicitações da api
class APIRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, content_type='application/json', status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        item_id = self.path.split("/")
        #Verifica se um item especifico consta no estoque
        if item_id[1] == 'id':
            if item_id[2] in dados:
                self._set_response()
                self.wfile.write(json.dumps(dados[item_id[2]]).encode('utf-8'))
            else:
                self.send_response(204)
                self.end_headers()
                self.wfile.write(b'Produto nao presente no estoque')
        #Chama o carrinho de compras de um caixa espefifico
        elif item_id[1] == 'visualizar_carrinho':
            caixa = int(item_id[2])
            if caixa in carrinho_compras:
                self._set_response()
                self.wfile.write(json.dumps(carrinho_compras[caixa]).encode('utf-8'))
            else:
                self.send_response(204)
                self.end_headers()
                self.wfile.write(b'Nenhum item adicionado ao carrinho')
        #Chama o histórico geral de compras de todos os caixas
        elif item_id[1] == 'historico_geral':
            self.wfile.write(json.dumps(historico_geral_compras).encode('utf-8'))

        else:
            self._set_response('text/plain', 404)
            self.wfile.write(b'Endpoint not found')
        
        
    def do_POST(self):
        item_id = self.path.split("/")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        #Adiciona um item ao carrinho de compras de um caixa especifico
        if item_id[1] == 'carrinho': 
            try:
                # Tente analisar os dados JSON
                json_data = json.loads(post_data.decode('utf-8'))
                
                #Adiciona os itens do pedido no carrinho
                print('Dados JSON recebidos:', json_data)
                if json_data['port'] not in carrinho_compras:
                    carrinho_compras[json_data['port']] = {json_data['tag'] : json_data['pedido']}
                    carrinho_compras[json_data['port']][json_data['tag']]['Quant'] = 1
                else:
                    
                    if json_data['tag'] in carrinho_compras[json_data['port']]:
                        carrinho_compras[json_data['port']][json_data['tag']]['Quant'] += 1
                        carrinho_compras[json_data['port']][json_data['tag']]['Val'] += dados[json_data['tag']]['Val']
                    else:
                        carrinho_compras[json_data['port']][json_data['tag']] = json_data['pedido']
                        carrinho_compras[json_data['port']][json_data['tag']]['Quant'] = 1
                
                # Responda com sucesso
                self._set_response()
                self.wfile.write(b'Sucesso')
        
            except ValueError as e:
                # Se houver um erro ao analisar os dados JSON, responda com um erro
                self._set_response('text/plain', 400)
                self.wfile.write(f'Erro na análise JSON: {e}'.encode('utf-8'))
        #Verifica a disponibilidade de itens, finaliza uma compra, limpa o carrinho e adiciona a compra ao histórico geral
        if item_id[1] == 'compra':
            try:
                carrinho_temporario = []
                # Tente analisar os dados JSON
                json_data = json.loads(post_data.decode('utf-8'))

                if json_data['caixa'] in carrinho_compras:
                    for i in carrinho_compras[json_data['caixa']]:
                        if i in dados:
                         
                            if carrinho_compras[json_data['caixa']][i]['Quant'] > dados[i]['Quant']:
                                carrinho_temporario.append(False)
                            else:
                                carrinho_temporario.append(True)
                        else:
                            #Limpar o carrinho
                            limpar_carrinho(json_data['caixa'])
                            self._set_response(204)
                            self.wfile.write(b'error')
                            
                    if False in carrinho_temporario:
                        limpar_carrinho(json_data['caixa'])
                        self._set_response(204)
                        self.wfile.write(b'error')
                    else:                        
                        for i in carrinho_compras[json_data['caixa']]:
                            if i in dados:
                                dados[i]['Quant'] -= carrinho_compras[json_data['caixa']][i]['Quant']
                        
                        #Adiciona no histórico geral
                        if json_data['caixa'] not in historico_geral_compras:
                            historico_geral_compras[json_data['caixa']] = {1 : carrinho_compras[json_data['caixa']]}
                        else:
                            contagem = len(historico_geral_compras[json_data['caixa']])
                            historico_geral_compras[json_data['caixa']][contagem + 1] = carrinho_compras[json_data['caixa']]

                        #Limpar o carrinho
                        limpar_carrinho(json_data['caixa'])
                        
                        # Responda com sucesso
                        self._set_response()
                        self.wfile.write(b'Sucesso')
                
                print('Dados JSON recebidos:', json_data)
        
            except ValueError as e:
                # Se houver um erro ao analisar os dados JSON, responda com um erro
                self._set_response('text/plain', 400)
                self.wfile.write(f'Erro na análise JSON: {e}'.encode('utf-8'))
        #Altera o acesso dos caixas ao servidor
        if item_id[1] == 'acesso_caixa':
            try:
                json_data = json.loads(post_data.decode('utf-8'))
                if json_data['caixa'] in caixas:
                    if caixas[json_data['caixa']] == 'Ativo':
                        caixas[json_data['caixa']] = 'Inativo'
                    else:
                        caixas[json_data['caixa']] = 'Ativo'
                print(caixas)
                 # Responda com sucesso
                self._set_response()
                self.wfile.write(b'Sucesso')
            except ValueError as e:
                # Se houver um erro ao analisar os dados JSON, responda com um erro
                self._set_response('text/plain', 400)
                self.wfile.write(f'Erro na análise JSON: {e}'.encode('utf-8'))
        #Verifica o acesso dos caixas ao servidor
        if item_id[1] == 'verifica_caixa':
            try:
                json_data = json.loads(post_data.decode('utf-8'))

                #Verifica se o caixa já está registrado, se não estiver, ele registra
                if json_data['caixa'] not in caixas:
                    caixas[json_data['caixa']] = 'Ativo'
                    print(caixas)
                if caixas[json_data['caixa']] == 'Ativo':
                 # Responda com sucesso
                    self._set_response()
                    self.wfile.write(b'Sucesso')
                else:
                    self.send_response(204)
                    self.end_headers()
                    self.wfile.write(b'Caixa bloequeado')
                    
            except ValueError as e:
                # Se houver um erro ao analisar os dados JSON, responda com um erro
                self._set_response('text/plain', 400)
                self.wfile.write(f'Erro na análise JSON: {e}'.encode('utf-8'))

        else:
            # Se o endpoint não for encontrado, responda com um erro 404
            self._set_response('text/plain', 404)
            self.wfile.write(b'Endpoint not found')
        
        
#Função responsável por limpar o carrinho
def limpar_carrinho(caixa):
    if caixa in carrinho_compras:
        carrinho_compras.pop(caixa)
    

def start(server_class=HTTPServer, handler_class=APIRequestHandler, port=3003):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}')
    httpd.serve_forever()
    
   
if __name__ == "__main__": 
    start()

