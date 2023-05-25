import bluetooth
import serial
import serial.tools.list_ports
from bluepy import btle

# Dirección Bluetooth del dispositivo Android
android_address = "6C:1E:D7:7A:7F:6E"

service_uuid = "00001801-0000-1000-8000-00805f9b34fb"

characteristic_uuid = "00001801-0000-1000-8000-00805f9b34fb"

# Conectarse al dispositivo Android
peripheral = btle.Peripheral(android_address)

service = peripheral.getServiceByUUID(service_uuid)
characteristic = service.getCharacteristics(characteristic_uuid)[0]

# Enviar un mensaje al dispositivo Android
message = "Hola desde la Raspberry Pi"
characteristic.write(bytes(message, "utf-8"), withResponse=True)

peripheral.disconnect()
