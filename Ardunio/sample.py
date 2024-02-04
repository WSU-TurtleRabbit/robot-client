import serial
from serial.tools import list_ports

def detect_ardunio_device():
    USBVID = [0x2341, 0x2a03]
    devices = list_ports.comports()
    devices = [x for x in devices if x.vid in USBVID]

    if not devices or len(devices) > 1:
        return None
    
    return devices[0].device

if __name__ == '__main__':
    port = detect_ardunio_device()
    # access serial device at /dev/cu.usbmodem101 using baudrate of 192000
    with serial.Serial(port, 19200) as s: 
        # write a 'K'
        while True:
            input()
            s.write(b'K')
        # release the serial device to avoid a 'device is busy' error
        s.close()