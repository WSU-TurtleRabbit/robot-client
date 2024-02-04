import serial
from serial.tools import list_ports

def detect_ardunio_device():
    vid = ''
    pid = '' 
    devices = list_ports.comports()
    devices = [x for x in devices if x.vid == vid and x.pid == pid]
   
    if not devices:
        raise ValueError(f"no ardunio devices not found")
    
    if len(devices) > 1:
        raise ValueError(f"found {len(devices) }ardunio devices")
    
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