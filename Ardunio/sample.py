import serial

if __name__ == '__main__':
    with serial.Serial('/dev/cu.usbmodem101', 19200) as s:
        s.write(b'K')
        s.close()
            
