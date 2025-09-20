import serial
import time
import os

# Wait until modem device appears (after BOOT button is pressed)
def wait_for_modem_device():
    print("Waiting for modem to appear...")
    while not os.path.exists("/dev/ttyUSB2"):
        time.sleep(1)
    print("Modem device found.")

# Serial connection to Nextion display
nextion = serial.Serial('/dev/ttyS0', 9600, timeout=1)

# Wait for modem to be available
wait_for_modem_device()

# Serial connection to SIM7600G-H modem
time.sleep(2)
modem = serial.Serial('/dev/ttyUSB2', 115200, timeout=1)

def unlock_sim(pin="9699"):
    modem.write(b'AT+CPIN?\r')
    time.sleep(1)
    response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
    if "SIM PIN" in response:
        modem.write(f'AT+CPIN="{pin}"\r'.encode())
        time.sleep(2)
        response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
        print("SIM PIN sent. Response:", response)
    elif "READY" in response:
        print("SIM already unlocked.")
    else:
        print("SIM status unknown:", response)

def wait_for_ready():
    for _ in range(20):
        modem.write(b'AT+CPIN?\r')
        time.sleep(1)
        response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
        if "READY" in response:
            print("SIM is ready.")
            break
    for _ in range(20):
        modem.write(b'AT+CREG?\r')
        time.sleep(1)
        response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
        if "0,1" in response or "0,5" in response:
            print("Modem registered to network.")
            break

def set_voice_mode():
    modem.write(b'AT+QCFG="callmode",0\r')
    time.sleep(1)
    modem.write(b'AT+CFUN=1,1\r')  # Reboot modem
    print("Switched to voice mode and rebooted modem.")
    time.sleep(10)

def normalize_number(number):
    if number.startswith("0"):
        return "+385" + number[1:]
    return number

def is_valid_number(number):
    return number.isdigit() and len(number) >= 8

def read_number_from_nextion():
    data = nextion.readline().decode('utf-8', errors='ignore').strip()
    if is_valid_number(data):
        return data
    return None

def dial_number(number):
    number = normalize_number(number)
    at_command = f"ATD{number};\r"
    modem.write(at_command.encode())
    print(f"Calling: {number}")

def listen_for_hangup():
    data = nextion.readline().decode('utf-8', errors='ignore').strip()
    if data == "HANGUP":
        modem.write(b'AT+CHUP\r\n')
        send_nextion_command("page page0")
        print("Call ended.")

def send_nextion_command(command):
    nextion.write(command.encode() + b'\xff\xff\xff')
    time.sleep(0.1)

def show_incoming_call_on_nextion(number):
    send_nextion_command("page page1")
    time.sleep(0.2)
    send_nextion_command(f't0.txt="{number}"')
    print(f"Incoming call from: {number}")

def check_for_incoming_call():
    modem.write(b'AT+CLIP=1\r')  # Enable caller ID
    time.sleep(0.5)
    response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
    if "RING" in response and "+CLIP:" in response:
        lines = response.splitlines()
        for line in lines:
            if "+CLIP:" in line:
                parts = line.split('"')
                if len(parts) > 1:
                    number = parts[1]
                    return number
    return None

# Startup sequence
unlock_sim("9699")
wait_for_ready()
set_voice_mode()
wait_for_ready()

# Main loop
while True:
    listen_for_hangup()

    if nextion.in_waiting:
        phone_number = read_number_from_nextion()
        if phone_number and is_valid_number(phone_number):
            dial_number(phone_number)
        elif phone_number:
            print("Invalid phone number.")

    incoming_number = check_for_incoming_call()
    if incoming_number:
        show_incoming_call_on_nextion(incoming_number)

    time.sleep(0.5)
