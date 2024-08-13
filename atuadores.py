import socket
import threading

def atuador_client(atuador_id, atuador_type):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9999))
    
    # Identifica o atuador para o Gerenciador
    identificacao = f"Tipo:IDENTIFICACAO_ATUADOR;Atuador_ID:{atuador_id};Atuador_Tipo:{atuador_type}"
    client.send(identificacao.encode('utf-8'))
    ack = client.recv(1024).decode('utf-8')
    print(f"[+] Atuador {atuador_id} ({atuador_type}) identificado com sucesso: {ack}")
    
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                continue  # Espera por novas mensagens se a atual estiver vazia
            
            parts = dict(item.split(":") for item in message.split(";"))
            comando = parts.get("Comando")
            
            if comando == "LIGAR":
                print(f"[+] {atuador_type} {atuador_id} ligado")
            elif comando == "DESLIGAR":
                print(f"[+] {atuador_type} {atuador_id} desligado")
        except ConnectionResetError:
            print(f"[+] Conexão perdida com o Gerenciador")
            break
        except Exception as e:
            print(f"[+] Erro: {str(e)}")
            break

    client.close()

def start_atuators():
    atuators = [
        {"id": "aquecedor1", "tipo": "Aquecedor"},
        {"id": "resfriador1", "tipo": "Resfriador"},
        {"id": "irrigacao1", "tipo": "Irrigacao"},
        {"id": "injetor_co2", "tipo": "Injetor_CO2"}
    ]
    
    threads = []

    for atuador in atuators:
        t = threading.Thread(target=atuador_client, args=(atuador["id"], atuador["tipo"]))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    start_atuators()
