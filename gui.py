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
        self.resize(800, 600)  # Ajusta el tamanio de la ventana

        # Crear pestanias
        self.tab_widget = QTabWidget()
        self.bluetooth_tab = QWidget()
        self.agendaTel_tab = QWidget()
        self.conect_tab = QWidget()

        self.tab_widget.addTab(self.conect_tab, "Connect")
        self.tab_widget.addTab(self.bluetooth_tab, "Configuracion")
        self.tab_widget.addTab(self.agendaTel_tab, "Descargar Datos")

        # Organizar widgets de la pestania Connect
        conect_layout = QVBoxLayout()
        
        self.conect_tab.setLayout(conect_layout)
        
        scan_button = QPushButton("Escanear")
        set_button = QPushButton("Set Target")
        conect_button = QPushButton("Conectar")
        
        clon_button = QPushButton("Clonar")
        
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


        # Organizar widgets de la pestania Bluetooth
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


        # Organizar widgets de la ventana de descarga telefonica
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

        # Conectar seniales y slots
        conect_button.clicked.connect(self.conect_device)
        set_button.clicked.connect(self.setTarget)
        update_button.clicked.connect(self.update_bluetooth_config)
        scan_button.clicked.connect(self.scan_devices)
        clon_button.clicked.connect(self.clon_devices)
        descarga_button.clicked.connect(self.descarga_agenda)
        desMsg_button.clicked.connect(self.descarga_sms)

    def conect_device(self):
        self.agent_daemon()
        item = self.scan_list.currentItem()
        if item:
            item_index = self.scan_list.row(item)  # Obtener el índice del elemento en la lista
            mac_address = self.mac_addresses.get(item_index, "")
            name = self.name_entry.text()
            class_of_device = self.class_of_devices.get(item_index, "")
        self.target_mac = mac_address
        self.target_name = name
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((mac_address, 1))

    def setTarget(self):
        self.agent_daemon()
        item = self.scan_list.currentItem()
        if item:
            item_index = self.scan_list.row(item)  # Obtener el índice del elemento en la lista
            mac_address = self.mac_addresses.get(item_index, "")
            name = self.name_entry.text()
            class_of_device = self.class_of_devices.get(item_index, "")
        self.target_mac = mac_address
        self.target_name = name
            
    def update_bluetooth_config(self):
        name = self.name_entry.text()
        address = self.address_entry.text()
        cod = self.classm_entry.text()

        updateName.clone_device(address,name,int(cod))

    def scan_devices(self):
        tiempo = self.time_entry.text()
        self.ubertooth_scanner.start_scan(duration=tiempo)
        devices = self.ubertooth_scanner.get_devices()
        self.scan_list.clear()
        self.mac_addresses = {}  # Diccionario para almacenar las MAC addresses por nombre
        self.class_of_devices = {}  # Diccionario para almacenar las Class of Device por nombre
        
        self.item_counter = 0  # Reiniciar el contador
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
        item = self.scan_list.currentItem()
        if item:
            item_index = self.scan_list.row(item)  # Obtener el índice del elemento en la lista
            mac_address = self.mac_addresses.get(item_index, "")
            name = self.name_entry.text()
            class_of_device = self.class_of_devices.get(item_index, "")
            print(mac_address)
            print(name)
            print(class_of_device)
        updateName.clone_device(mac_address, name, class_of_device)

    def agent_daemon(self):
        print("Ejecutar agente NoInputNoOutput como daemon")
        subprocess.run(["bt-agent", "-c", "NoInputNoOutput", "-d"])

    def descarga_agenda(self):
        target = self.target_mac
        tabla = self.target_name
        pbapclient.main(target,tabla)
        createDatabase.createTableContacts(tabla)
    def descarga_sms(self):
        target = self.target_mac
        tabla = self.target_name
        mapclient.main(target,tabla)
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
