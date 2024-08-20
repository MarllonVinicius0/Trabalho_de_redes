import socket

def listar_sensores(client_socket):
    client_socket.send("Tipo:LISTAR_SENSORES".encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    sensores = response.split(";")
    print("\nLista de Sensores:")
    if sensores:
        for sensor in sensores:
            if sensor:
                id_tipo = sensor.split(",")
                if len(id_tipo) == 2:
                    print(f"ID: {id_tipo[0]} Tipo: {id_tipo[1]}")
    else:
        print("Nenhum sensor encontrado.")

def listar_atuadores(client_socket):
    client_socket.send("Tipo:LISTAR_ATUADORES".encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    atuadores = response.split(";")
    print("\nLista de Atuadores:")
    if atuadores:
        for atuador in atuadores:
            if atuador:
                id_tipo = atuador.split(",")
                if len(id_tipo) == 2:
                    print(f"ID: {id_tipo[0]} Tipo: {id_tipo[1]}")
    else:
        print("Nenhum atuador encontrado.")

def requisitar_dados(client_socket):
    print("\nEscolha o tipo de dado:")
    print("1. Sensor")
    print("2. Atuador")
    choice = input("Digite o número da opção desejada: ")
    
    if choice == "1":
        listar_sensores(client_socket)
        sensor_id = input("Digite o ID do sensor para requisitar dados: ")
        message = f"Tipo:GET_SENSOR_DATA;Sensor_ID:{sensor_id}"
        client_socket.send(message.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(f"\nDados do Sensor {sensor_id}: {response}")

    elif choice == "2":
        listar_atuadores(client_socket)
        atuador_id = input("Digite o ID do atuador para requisitar dados: ")
        message = f"Tipo:GET_ACTUATOR_DATA;Atuador_ID:{atuador_id}"
        client_socket.send(message.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(f"\nDados do Atuador {atuador_id}: {response}")

    else:
        print("Opção inválida.")

def enviar_comando(client_socket):
    print("\nEscolha o tipo de comando:")
    print("1. Sensor (Alterar Limites)")
    print("2. Atuador (Ligar/Desligar)")
    choice = input("Digite o número da opção desejada: ")

    if choice == "1":
        listar_sensores(client_socket)
        sensor_tipo = input("Digite o tipo do sensor para alterar os limites: ")
        min_val = input("Digite o valor mínimo: ")
        max_val = input("Digite o valor máximo: ")
        message = f"Tipo:SET_SENSOR_LIMITS;Sensor_Tipo:{sensor_tipo};Min:{min_val};Max:{max_val}"
        client_socket.send(message.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(f"\nResposta do servidor: {response}")
        
    elif choice == "2":
        listar_atuadores(client_socket)
        atuador_id = input("Digite o ID do atuador para enviar o comando: ")
        comando = input("Digite o comando (LIGAR/DESLIGAR): ")
        message = f"Tipo:CONTROL;Atuador_ID:{atuador_id};Comando:{comando}"
        client_socket.send(message.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(f"\nResposta do servidor: {response}")
        
    else:
        print("Opção inválida.")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9999))

    while True:
        print("\nMenu:")
        print("1. Requisitar Dados")
        print("2. Enviar Comando")
        print("3. Sair")
        option = input("Escolha uma opção: ")

        if option == "1":
            requisitar_dados(client_socket)
        elif option == "2":
            enviar_comando(client_socket)
        elif option == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")
    
    client_socket.close()

if __name__ == "__main__":
    main()
