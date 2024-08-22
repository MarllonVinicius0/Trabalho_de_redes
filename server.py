import socket
import threading

# Dados dos sensores e atuadores armazenados no gerenciador
sensor_data = {}
atuador_commands = {}

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
        atuador_id = parts.get("Atuador_ID")
        atuador_tipo = parts.get("Atuador_Tipo")
        atuador_commands[atuador_id] = {"tipo": atuador_tipo, "comando": "DESLIGAR"}
        print(f"[+] Atuador {atuador_id} ({atuador_tipo}) identificado")
        client_socket.send(f"ACK_ATUADOR;Atuador_ID:{atuador_id}".encode('utf-8'))

    elif msg_type == "LISTAR_SENSORES":
        response = ";".join([f"{sensor_id},{info['tipo']}" for sensor_id, info in sensor_data.items()])
        client_socket.send(response.encode('utf-8'))
        
    elif msg_type == "LISTAR_ATUADORES":
        response = ";".join([f"{atuador_id},{info['tipo']}" for atuador_id, info in atuador_commands.items()])
        client_socket.send(response.encode('utf-8'))

    elif msg_type == "GET_SENSOR_DATA":
        sensor_id = parts.get("Sensor_ID")
        value = sensor_data.get(sensor_id, {}).get("valor", "N/A")
        response = f"SENSOR_DATA;Sensor_ID:{sensor_id};Valor:{value}"
        client_socket.send(response.encode('utf-8'))
        print(f"[+] Enviando resposta: {response}")
        
    elif msg_type == "GET_ACTUATOR_DATA":
        atuador_id = parts.get("Atuador_ID")
        command = atuador_commands.get(atuador_id, {}).get("comando", "N/A")
        response = f"ACTUATOR_DATA;Atuador_ID:{atuador_id};Comando:{command}"
        client_socket.send(response.encode('utf-8'))
        print(f"[+] Enviando resposta: {response}")

    elif msg_type == "CONTROL":
        atuador_id = parts.get("Atuador_ID")
        comando = parts.get("Comando")
        if atuador_id in atuador_commands:
            atuador_commands[atuador_id]["comando"] = comando
            response = f"ACK_CONTROL;Atuador_ID:{atuador_id};Comando:{comando}"
            client_socket.send(response.encode('utf-8'))
            print(f"[+] Comando {comando} enviado para o atuador {atuador_id}")
        else:
            response = "ERRO;Atuador não encontrado"
            client_socket.send(response.encode('utf-8'))
            print("[+] Erro: Atuador não encontrado")
    
    elif msg_type == "SET_SENSOR_LIMITS":
        sensor_tipo = parts.get("Sensor_Tipo")
        min_val = float(parts.get("Min"))
        max_val = float(parts.get("Max"))
        
        if sensor_tipo in limites:
            limites[sensor_tipo]["min"] = min_val
            limites[sensor_tipo]["max"] = max_val
            response = f"ACK_LIMITS;Sensor_Tipo:{sensor_tipo};Min:{min_val};Max:{max_val}"
            print(f"[+] Limites do sensor {sensor_tipo} atualizados: Min={min_val}, Max={max_val}")
        else:
            response = "ERRO;Tipo de sensor não encontrado"
        
        client_socket.send(response.encode('utf-8'))

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

def send_command(atuador_type, command, client_socket):
    for atuador_id, atuador_info in atuador_commands.items():
        if atuador_info["tipo"] == atuador_type:
            atuador_commands[atuador_id]["comando"] = command
            comando = f"Tipo:CONTROL;Atuador_ID:{atuador_id};Comando:{command}"
            client_socket.send(comando.encode('utf-8'))
            print(f"[+] Enviando comando para {atuador_type}: {command}")

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
