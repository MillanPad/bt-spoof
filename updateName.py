import bluetooth
import classofdevice
import subprocess
import shlex
import fileinput
import re
def clone_device(mac_address,nombre,class_of_device):
    # Cambiar la direccion MAC con bdaddr
    comando_mac = ["sudo", "./bdaddr", "-r",mac_address]
    subprocess.run(comando_mac, capture_output=True)
    # Reinicia el servicio y el adaptador bluetooth para que se realicen los cambios
    comando_restart = ['sudo', 'systemctl', 'restart', 'bluetooth.service']
    subprocess.run(comando_restart, capture_output=True)

    change_bluetooth_name(nombre)
    
    change_class_of_device(class_of_device)



import dbus

def change_bluetooth_name(new_name):
    # Mediante dbus obtiene la interfaz bluetooth y el adaptador
    bus = dbus.SystemBus()
    adapter_path = '/org/bluez/hci0'  # Cambia el valor a la ruta correcta de tu adaptador
    adapter = dbus.Interface(bus.get_object('org.bluez', adapter_path), 'org.freedesktop.DBus.Properties')
    # Cambia el nombre del adaptador obtenido
    adapter.Set('org.bluez.Adapter1', 'Alias', dbus.String(new_name))

def change_class_of_device(new_class):
    #Ejecuta el comando hciconfig para cambiar el CoD del adaptador
    subprocess.run(['sudo','hciconfig','-a','hci0','class',hex(new_class)],capture_output=True)
