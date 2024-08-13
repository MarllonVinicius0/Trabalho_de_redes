import socket
import threading
import time
import random

def sensor_client(sensor_id, sensor_type):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9999))
    
    # Identifica o sensor para o Gerenciador
    identificacao = f"Tipo:IDENTIFICACAO_SENSOR;Sensor_ID:{sensor_id};Sensor_Tipo:{sensor_type}"
    client.send(identificacao.encode('utf-8'))
    ack = client.recv(1024).decode('utf-8')
    print(f"[+] Sensor {sensor_id} ({sensor_type}) identificado com sucesso: {ack}")
    
    while True:
        if sensor_type == "Temperatura":
            valor = round(random.uniform(15.0, 35.0), 2)  # Gera valores aleatórios de temperatura
        elif sensor_type == "Umidade":
            valor = round(random.uniform(20.0, 60.0), 2)  # Gera valores aleatórios de umidade
        elif sensor_type == "CO2":
            valor = round(random.uniform(300.0, 900.0), 2)  # Gera valores aleatórios de CO2
        
        message = f"Tipo:SENSOR_DATA;Sensor_ID:{sensor_id};Valor:{valor}"
        client.send(message.encode('utf-8'))
        print(f"[+] Sensor {sensor_id} enviou valor: {valor}")
        
        time.sleep(1)

def start_sensors():
    sensors = [
        {"id": "1", "tipo": "Temperatura"},
        {"id": "2", "tipo": "Umidade"},
        {"id": "3", "tipo": "CO2"}
    ]
    
    threads = []

    for sensor in sensors:
        t = threading.Thread(target=sensor_client, args=(sensor["id"], sensor["tipo"]))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

start_sensors()
