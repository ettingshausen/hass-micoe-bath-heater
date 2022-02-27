import serial as ser

HEX_MAP = {
    'Off': 'FD 03 51 B6 0C 30 DF',
    'Heat': 'FD 03 51 B6 04 30 DF',
    'Ventilate': 'FD 03 51 B6 01 30 DF',
    'Light': 'FD 03 51 B6 08 30 DF',
    'Night Light': 'FD 03 51 B6 02 30 DF',
    'Nature Wind': 'FD 03 51 B6 03 30 DF'
}


def turn_off():
    execute('Off')


def turn_light_up(option):
    if option == 'Light':
        execute('Light')
        return
    execute('Night Light')


def execute(option):
    se = ser.Serial("/dev/cu.usbserial-1430")
    to_bytes = bytes.fromhex(HEX_MAP.get(option))
    se.write(to_bytes)
    se.close()
