import sqlite3
import xml.etree.ElementTree as ET
import subprocess
import re
import shutil
from datetime import datetime

def createTableMsg(tabla,subfold):
    #Cargar el archivo XML para analizarlo
    tree = ET.parse(f'{tabla}/telecom/msg/{subfold}/mlisting.xml')
    root = tree.getroot()
    tabla = tabla+subfold
    # Crear la conexión a la base de datos y el cursor
    conn = sqlite3.connect('bt-project.sqlite')
    c = conn.cursor()

    # Verificar si la tabla ya existe
    c.execute(f"SELECT name FROM sqlite_master WHERE type=\'tables\' AND name='{tabla}'")
    table_exists = c.fetchone()

    if table_exists:
        pass
    else:
        # Crear la tabla si no existe
        c.execute(f"CREATE TABLE {tabla} (id INTEGER PRIMARY KEY AUTOINCREMENT, handle TEXT, subject VARCHAR(300), datetime TEXT, sender_name TEXT, sender_addressing TEXT, recipient_addressing TEXT, type TEXT)")
        print("vale")
    # Obtener el último id insertado
    c.execute(f"SELECT MAX(id) FROM {tabla}")
    last_id = c.fetchone()[0] or 0

    # Iterar sobre los elementos 'msg'
    for msg in root.findall('msg'):
        handle = msg.get('handle')
        subject = msg.get('subject')
        datetime_str = msg.get('datetime')
        sender_name = msg.get('sender_name')
        sender_addressing = msg.get('sender_addressing')
        recipient_addressing = msg.get('recipient_addressing')
        msg_type = msg.get('type')

        # Convertir el formato de fecha y hora a un objeto datetime
        datetime_obj = datetime.strptime(datetime_str, "%Y%m%dT%H%M%S")

        # Incrementar el id para el nuevo registro
        last_id += 1

        # Insertar los datos en la tabla
        c.execute(f"INSERT INTO {tabla} (handle, subject, datetime, sender_name, sender_addressing, recipient_addressing, type) VALUES ('{handle}', '{subject}', '{datetime_str}', '{sender_name}','{sender_addressing}', '{recipient_addressing}','{msg_type}')")

    # Confirmar los cambios y cerrar la conexión a la base de datos
    conn.commit()
    conn.close()
    #Elimina la carpeta creada durante la descarga
    shutil.rmtree(tabla)
def createTableContacts(tabla):
    #Cargar el archivo XML para analizarlo
    tree = ET.parse(f'{tabla}/telecom/pb/listing.xml')
    root = tree.getroot()
    # Crear la conexión a la base de datos y el cursor
    conn = sqlite3.connect('bt-project.sqlite')
    c = conn.cursor()
    # Verificar si la tabla ya existe
    c.execute(f"SELECT name FROM sqlite_master WHERE type=\'tables\' AND name='{tabla}'")
    table_exists = c.fetchone()

    if table_exists:
        pass
    else:
        # Crear la tabla si no existe
        c.execute(f"CREATE TABLE {tabla} (id INTEGER PRIMARY KEY, nombre TEXT, telefono TEXT)")
        
    # Obtener el último id insertado    
    c.execute(f"SELECT MAX(id) FROM {tabla}")
    last_id = c.fetchone()[0] or 0
    # Iterar sobre los elementos 'card'
    for card in root.findall('card'):
        handle = card.get('handle')
        name = card.get('name')
        #Abre el archivo correspondiente donde se encuentra el telefono 
        file = open(f'{tabla}/telecom/pb/{handle}', 'r')
        line = file.read()
        #Busca el telefono en caso de no tener prefijo
        match = re.search(r'TEL;CELL:(\d+)',line)
        if match:
            tel = match.group(1)
        else:
            #Si tiene prefijo de españa, solo coge el telefono sin prefijo
            match2 = re.search(r'TEL;CELL:\+34(\d+)',line)
            if match2:
                tel = match2.group(1)
            else:
                tel = None
        #Inserta los datos de la tabla
        c.execute(f"INSERT INTO {tabla} (nombre,telefono) VALUES ('{name}', '{tel}')")
        
    # Confirmar los cambios y cerrar la conexión a la base de datos    
    conn.commit()
    conn.close()
    #Elimina la carpeta creada durante la descarga
    shutil.rmtree(tabla)



