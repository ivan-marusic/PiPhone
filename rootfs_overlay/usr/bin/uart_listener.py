import serial

ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
number = ""

def send_to_nextion(text):
    command = f't0.txt="{text}"' + '\xff\xff\xff'
    ser.write(command.encode('utf-8'))

while True:
    if ser.in_waiting:
        data = ser.readline().decode('utf-8').strip()
        if data == "DEL":
            number = number[:-1]
        elif data == "CALL":
            print(f"Pozivanje broja: {number}")
        elif data.isdigit():
            number += data
        send_to_nextion(number)

