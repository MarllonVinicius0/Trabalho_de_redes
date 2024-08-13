import socket
import threading

# Dados dos sensores armazenados no gerenciador
sensor_data = {}
# Comandos para os atuadores armazenados no gerenciador
atuator_commands = {}
# Limites definidos para as condições da estufa
limites = {
    "Temperatura": {"min": 20.0, "max": 25.0},
    "Umidade": {"min": 30.0, "max": 50.0},
    "CO2": {"min": 400.0, "max": 800.0}
}

def handle_client(client_socket, address):
    print(f"[+] Nova conexão de {address}")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            print(f"[+] Mensagem recebida: {message}")
            process_message(message, client_socket)
        
        except ConnectionResetError:
            break

    client_socket.close()

def process_message(message, client_socket):
    parts = dict(item.split(":") for item in message.split(";"))
    msg_type = parts.get("Tipo")
    
    if msg_type == "IDENTIFICACAO_SENSOR":
        sensor_id = parts.get("Sensor_ID")
        sensor_tipo = parts.get("Sensor_Tipo")
        sensor_data[sensor_id] = {"tipo": sensor_tipo, "valor": None}
        print(f"[+] Sensor {sensor_id} ({sensor_tipo}) identificado")
        client_socket.send(f"ACK_SENSOR;Sensor_ID:{sensor_id}".encode('utf-8'))
        
    elif msg_type == "SENSOR_DATA":
        sensor_id = parts.get("Sensor_ID")
        valor = float(parts.get("Valor"))
        sensor_data[sensor_id]["valor"] = valor
        print(f"[+] Sensor {sensor_id} atualizado com valor {valor}")
        check_conditions(sensor_data[sensor_id]["tipo"], valor, client_socket)
        
    elif msg_type == "IDENTIFICACAO_ATUADOR":
        atuator_id = parts.get("Atuador_ID")
        atuator_tipo = parts.get("Atuador_Tipo")
        atuator_commands[atuator_id] = {"tipo": atuator_tipo, "comando": "DESLIGAR"}
        print(f"[+] Atuador {atuator_id} ({atuator_tipo}) identificado")
        client_socket.send(f"ACK_ATUADOR;Atuador_ID:{atuator_id}".encode('utf-8'))

    elif msg_type == "GET_SENSOR_DATA":
        sensor_id = parts.get("Sensor_ID")
        value = sensor_data.get(sensor_id, {}).get("valor", "N/A")
        response = f"SENSOR_DATA;Sensor_ID:{sensor_id};Valor:{value}"
        client_socket.send(response.encode('utf-8'))
        print(f"[+] Enviando resposta: {response}")

def check_conditions(sensor_type, valor, client_socket):
    min_val = limites[sensor_type]["min"]
    max_val = limites[sensor_type]["max"]
    
    if sensor_type == "Temperatura":
        if valor < min_val:
            send_command("Aquecedor", "LIGAR", client_socket)
            send_command("Resfriador", "DESLIGAR", client_socket)
        elif valor > max_val:
            send_command("Aquecedor", "DESLIGAR", client_socket)
            send_command("Resfriador", "LIGAR", client_socket)
        else:
            send_command("Aquecedor", "DESLIGAR", client_socket)
            send_command("Resfriador", "DESLIGAR", client_socket)
    
    elif sensor_type == "Umidade":
        if valor < min_val:
            send_command("Irrigacao", "LIGAR", client_socket)
        else:
            send_command("Irrigacao", "DESLIGAR", client_socket)
    
    elif sensor_type == "CO2":
        if valor < min_val:
            send_command("Injetor_CO2", "LIGAR", client_socket)
        else:
            send_command("Injetor_CO2", "DESLIGAR", client_socket)

def send_command(atuator_type, command, client_socket):
    for atuator_id, atuator_info in atuator_commands.items():
        if atuator_info["tipo"] == atuator_type:
            atuator_commands[atuator_id]["comando"] = command
            comando = f"Tipo:CONTROL;Atuador_ID:{atuator_id};Comando:{command}"
            client_socket.send(comando.encode('utf-8'))
            print(f"[+] Enviando comando para {atuator_type}: {command}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9999))
    server.listen(5)
    
    print("[+] Servidor iniciado e aguardando conexões...")
    
    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

start_server()
