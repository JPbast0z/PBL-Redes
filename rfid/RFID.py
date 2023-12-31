#!/usr/bin/env python3
import mercury
import sys
from datetime import datetime
import socket
import json
PORT_RFID = 7890
HOST= '172.16.103.0' #Tem que trocar o ip de acordo com o computador



def enviar_tags(servidor_rfid): 
        try:     
                param = 2300
                if len(sys.argv) > 1:
                        param = int(sys.argv[1])

                # configura a leitura na porta serial onde esta o sensor
                reader = mercury.Reader("tmr:///dev/ttyUSB0")

                # para funcionar use sempre a regiao "NA2" (Americas)
                reader.set_region("NA2")

                # nao altere a potencia do sinal para nao prejudicar a placa
                reader.set_read_plan([1], "GEN2", read_power=param)

                # realiza a leitura das TAGs proximas e imprime na tela
                # print(reader.read())

                epcs = map(lambda tag: tag, reader.read())

                lista_tags = []
                for tag in epcs:
                        print(tag.epc, tag.read_count, tag.rssi, datetime.fromtimestamp(tag.timestamp))
                        codigo_tag = (tag.epc).decode()
                        lista_tags.append(codigo_tag)
                lista_tags = json.dumps(lista_tags)

                servidor_rfid.send(lista_tags.encode())
                servidor_rfid.close()
                
        except socket.error as e:
                print("Erro de soquete:", e)
#Instancia a conexão com os caixas
def main():
        servidor_rfid = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #objeto socket IPV4 e TCP
        servidor_rfid.bind((HOST, PORT_RFID)) #vinculando o socket (servidor e a porta)
        servidor_rfid.listen() #Entrando no modo de escuta
        print('Ouvindo no host: ', HOST, ' na porta', PORT_RFID) #mensagem informando que a conexão foi aceita

        while True:
             conn, ender = servidor_rfid.accept() #retorno da conexão, conexão e endereço
             print(f'Conexão aceita com {ender}')
             enviar_tags(conn)

if __name__ == "__main__": 
    main()
