import subprocess

def obtener_mac_bluetooth():
    output = subprocess.check_output(['hciconfig'])
    output = output.decode('utf-8')
    mac_address = None

    # Buscar la dirección MAC en la salida de 'hciconfig'
    lines = output.split('\n')
    for line in lines:
        if 'BD Address' in line:
            mac_address = line.split('BD Address: ')[1]
            break

    return mac_address

