import bluetooth
import classofdevice
import subprocess
import shlex
import fileinput
import re
def clone_device(mac_address,nombre,class_of_device):
    #mac_address = ''.join(c for c in mac_address if c.isalnum())
    print(mac_address)
    # Cambiar la direccion MAC con bdaddr
    comando_mac = ["sudo", "./bdaddr", "-r",mac_address]
    subprocess.run(comando_mac, capture_output=True)

    comando_restart = ['sudo', 'systemctl', 'restart', 'bluetooth.service']
    subprocess.run(comando_restart, capture_output=True)

    change_bluetooth_name(nombre)
    
    change_class_of_device(class_of_device)



import dbus

def change_bluetooth_name(new_name):
    bus = dbus.SystemBus()
    adapter_path = '/org/bluez/hci0'  # Cambia el valor a la ruta correcta de tu adaptador
    adapter = dbus.Interface(bus.get_object('org.bluez', adapter_path), 'org.freedesktop.DBus.Properties')
    adapter.Set('org.bluez.Adapter1', 'Alias', dbus.String(new_name))

def change_class_of_device(new_class):
    subprocess.run(['sudo','hciconfig','-a','hci0','class',hex(new_class)],capture_output=True)
