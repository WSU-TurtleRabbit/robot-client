import serial

if __name__ == '__main__':
    # access serial device at /dev/cu.usbmodem101 using baudrate of 192000
    with serial.Serial('/dev/cu.usbmodem101', 19200) as s: 
        # write a 'K'
        s.write(b'K')
        # release the serial device to avoid a 'device is busy' error
        s.close()