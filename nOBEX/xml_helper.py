from xml.etree import ElementTree

def escape_ampersands(s):
    us = str(s, encoding='utf-8')
    us2 = '&amp;'.join(us.split('&'))
    return bytes(us2, encoding='utf-8')

def parse_xml(xml_str):
    try:
        root = ElementTree.fromstring(xml_str)
    except ElementTree.ParseError:
        root = ElementTree.fromstring(escape_ampersands(xml_str))
    return root
