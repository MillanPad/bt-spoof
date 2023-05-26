import bluetooth

class BluetoothScanner:
    def __init__(self):

        self.results = []


    def start_scan(self, duration):
        # Escaneo de dispositivos bluetooth cercanos y los guarda en una lista con su direccion bluetooth, nombre y CoD
        duration = int(duration)
        nearby_devices = bluetooth.discover_devices(duration=duration, lookup_names=True, lookup_class=True)
        for (addr, name, cl) in nearby_devices:
            self.results.append([addr, name, cl])

    def get_devices(self):
        #Retorna la lista de objetos
        return self.results

