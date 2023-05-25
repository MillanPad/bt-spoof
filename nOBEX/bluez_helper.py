
import atexit, socket, subprocess
import xml.etree.ElementTree as ET

def BluetoothSocket():
    return socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM,
            socket.BTPROTO_RFCOMM)

BDADDR_ANY = socket.BDADDR_ANY

class SDPException(Exception):
    pass

def get_available_port(address=BDADDR_ANY):
    for c in range(1, 31):
        s = BluetoothSocket()
        try:
            s.bind((address, c))
        except OSError:
            s.close()
        else:
            s.close()
            return c

    raise SDPException("All ports are in use!")


adv_services = set()

def stop_all():
    while len(adv_services):
        sn = adv_services.pop()
        stop_advertising(sn, False)

atexit.register(stop_all)

def subrun(args, stdout=None):
    if hasattr(subprocess, "run"):
        return subprocess.run(args, stdout=stdout)
    else:
        class SubrunResult(object):
            def __init__(self, retcode=0, output=None):
                self.returncode = retcode
                self.output = output

        if stdout:
            try:
                output = subprocess.check_output(args)
            except subprocess.CalledProcessError as e:
                return SubrunResult(e.returncode, e.output)
            else:
                return SubrunResult(0, output)
        else:
            ret = subprocess.call(args)
            return SubrunResult(ret)

def advertise_service(name, channel):
    name = name.upper()
    if name in adv_services:
        raise SDPException("Can't re-advertise a service")

    val = subrun(["sdptool", "add", "--channel=%i" % channel, name],
            stdout=subprocess.PIPE)
    if val.returncode != 0:
        raise SDPException("sdptool add returned %i" % val.returncode)
    adv_services.add(name)

def stop_advertising(name, pop=True):
    name = name.upper()
    if pop and not name in adv_services:
        return

    h, c = _search_record(name, "local")
    val = subrun(["sdptool", "del", h], stdout=subprocess.PIPE)
    if val.returncode != 0:
        raise SDPException("sdptool del returned %i" % val.returncode)

    if pop:
        adv_services.remove(name)

def find_service(name, bdaddr):
    h, c = _search_record(name, bdaddr)
    return c

def _search_record(name, bdaddr):
    val = subrun(
            ["sdptool", "search", "--xml", "--bdaddr=%s" % bdaddr, name],
            stdout=subprocess.PIPE)
    if val.returncode != 0:
        raise SDPException("sdptool search returned %i" % val.returncode)

    xml_lines = []
    for line in val.stdout.splitlines():
        if line.startswith(b'<') or line.startswith(b'\t'):
            xml_lines.append(line)
    xml_str = b''.join(xml_lines)

    serv_count = xml_str.count(b'<record>')
    if serv_count < 1:
        raise SDPException("Service %s not found on %s" % (name, bdaddr))
    elif serv_count > 1:
        xml_str = xml_str[:xml_str.index(b'</record>') + 9]

    try:
        tree = ET.fromstring(xml_str)
    except ET.ParseError:
        raise SDPException("Error parsing XML SDP record")
    if name.upper() == "HF":
        serv_classes = set()
        sc_attr = _find_attr(tree, "0x0001")[0]
        for c_elem in sc_attr.findall("uuid"):
            serv_classes.add(int(c_elem.attrib["value"], 16))
        if 0x111f in serv_classes:
            raise SDPException("HF on %s is HFAG" % bdaddr)


    handle = _find_attr(tree, "0x0000")[0].attrib["value"]
    channel = int(_find_attr(tree, "0x0004")[0][1][1].attrib["value"], 16)
    return handle, channel

def _find_attr(xml_tree, attr_id):
    for elem in xml_tree:
        if elem.tag == "attribute" and elem.attrib["id"] == attr_id:
            return elem
    raise SDPException("Attribute %s not found!" % attr_id)

_bluez_version_verified = False

def _verify_bluez_version():
    val = subrun(["bluetoothctl", "-v"], stdout=subprocess.PIPE)
    if val.returncode != 0:
        raise SDPException("Failed to get bluez version! Error: %i" % val.returncode)
    verstr = val.stdout[14:-1]
    smajor, sminor = verstr.split(b'.')
    major = int(smajor)
    minor = int(sminor)
    if (major < 5) or (major == 5 and minor < 49):
        raise SDPException("bluez 5.49 or newer required! you have bluez %i.%i" % (major, minor))

    global _bluez_version_verified
    _bluez_version_verified = True

def list_paired_devices():
    if not _bluez_version_verified:
        _verify_bluez_version()

    devs = set()

    val = subrun(["bluetoothctl", "paired-devices"], stdout=subprocess.PIPE)
    if val.returncode != 0:
        raise SDPException("bluetoothctl paired-devices returned %i" % val.returncode)


    for line in val.stdout.splitlines():
        fields = line.rstrip().split()
        devs.add(fields[1].decode('latin-1'))

    return devs
