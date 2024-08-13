import socket

def client_request(sensor_type):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9999))
    
    request = f"Tipo:GET_SENSOR_DATA;Sensor_Tipo:{sensor_type}"
    client.send(request.encode('utf-8'))
    
    response = client.recv(1024).decode('utf-8')
    print(f"[+] Resposta do servidor: {response}")
    
    client.close()

# Exemplo: Solicita dados do sensor de temperatura
client_request("Temperatura")
