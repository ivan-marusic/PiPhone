import serial
import time
import os

def wait_for_modem_device():
    print("Waiting for modem to appear...")
    while not os.path.exists("/dev/ttyUSB2"):
        time.sleep(1)
    print("Modem device found.")

nextion = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
wait_for_modem_device()
modem = serial.Serial('/dev/ttyUSB2', 115200, timeout=1)

def unlock_sim(modem, pin="9699"):
    modem.write(b"AT+CPIN?\r")
    time.sleep(1)
    response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
    print("CPIN response:", response)
    if "SIM PIN" in response:
        modem.write(f'AT+CPIN="{pin}"\r'.encode())
        time.sleep(2)
        response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
        print("SIM PIN sent. Response:", response)
    elif "READY" in response:
        print("SIM already unlocked.")
    else:
        print("SIM status unknown:", response)

def wait_for_ready(modem, pin="9699"):
    for _ in range(20):
        modem.write(b"AT+CPIN?\r")
        time.sleep(1)
        response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
        print("CPIN check:", response)
        if "SIM PIN" in response:
            print("SIM requires PIN, sending...")
            modem.write(f'AT+CPIN="{pin}"\r'.encode())
            time.sleep(2)
        elif "READY" in response:
            print("SIM is ready.")
            break
    for _ in range(20):
        modem.write(b"AT+CREG?\r")
        time.sleep(1)
        response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
        print("CREG check:", response)
        if "0,1" in response or "0,5" in response:
            print("Modem registered to network.")
            break

def set_voice_mode(modem):
    modem.write(b'AT+QCFG="callmode",0\r')
    time.sleep(1)
    modem.write(b"AT+CFUN=1,1\r")
    print("Switched to voice mode and rebooted modem.")
    modem.close()
    time.sleep(10)
    wait_for_modem_device()
    return serial.Serial('/dev/ttyUSB2', 115200, timeout=1)

def normalize_number(number):
    if number.startswith("0"):
        return "+385" + number[1:]
    elif number.startswith("+"):
        return number
    else:
        # fallback: assume already international
        return number

def is_valid_number(number):
    return number.isdigit() and len(number) >= 9 and number.startswith("0")

def read_number_from_nextion():
    if nextion.in_waiting:
        data = nextion.readline().decode('utf-8', errors='ignore').strip()
        print("Nextion input:", data)
        if data == "HANGUP":
            return None  # Or handle hangup elsewhere
        if is_valid_number(data):
            return data
    return None

def dial_number(modem, number):
    number = normalize_number(number)
    print(f"Dialing normalized number: {number}")
    at_command = f"ATD{number};\r"
    print("Sending AT command:", at_command)
    modem.write(at_command.encode())
    time.sleep(2)
    response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
    print("Dial response:", response)

def listen_for_hangup(modem):
    data = nextion.readline().decode('utf-8', errors='ignore').strip()
    if data == "HANGUP":
        modem.write(b"AT+CHUP\r\n")
        send_nextion_command("page page0")
        print("Call ended.")
	# Clear buffers and re-enable CLIP
        modem.reset_input_buffer()
        modem.reset_output_buffer()
        modem.write(b"AT+CLIP=1\r")

def listen_for_answer(modem):
    data = nextion.read(5)  # Reads 5 bytes
    if data == b'ANSW\n' or data == b'ANSWER\n':
        modem.write(b'ATA\r\n')  # Response to call
        print("Call accepted.")


def send_nextion_command(command):
    nextion.write(command.encode() + b'\xff\xff\xff')
    time.sleep(0.1)

def show_incoming_call_on_nextion(number):
    send_nextion_command("page page1")
    time.sleep(0.2)
    send_nextion_command(f't0.txt="{number}"')
    print(f"Incoming call from: {number}")

def check_for_incoming_call(modem):
    modem.write(b"AT+CLIP=1\r")
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

def check_call_end(modem):
    if modem.in_waiting:
        response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
        if "NO CARRIER" in response:
            print("Call ended by remote party.")
            modem.reset_input_buffer()
            modem.reset_output_buffer()
            modem.write(b"AT+CLIP=1\r")
            send_nextion_command("page page0")

# Startup sequence
unlock_sim(modem, "9699")
wait_for_ready(modem, "9699")
modem = set_voice_mode(modem)
wait_for_ready(modem, "9699")

def hangup_call(modem):
    modem.write(b"AT+CHUP\r\n")
    print("Sent AT+CHUP to modem.")
    time.sleep(1)
    if modem.in_waiting:
        response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
        print("Modem response after hangup:", response)
        if "NO CARRIER" in response:
            print("Call ended (NO CARRIER received).")
            modem.reset_input_buffer()
            modem.reset_output_buffer()
            modem.write(b"AT+CLIP=1\r")
            send_nextion_command("page page0")


# Main loop
while True:
    # 1. Handle Nextion input (number, HANGUP, ANSWER)
    if nextion.in_waiting:
        data = nextion.readline().decode('utf-8', errors='ignore').strip()
        print("Nextion input:", data)
        if data == "HANGUP":
            hangup_call(modem)  # See function below
        elif data == "ANSWER":
            modem.write(b'ATA\r\n')
           
            print("Call accepted.")
        elif is_valid_number(data):
            dial_number(modem, data)
        else:
            print("Invalid input from Nextion:", data)

    # 2. Handle incoming call
    incoming_number = check_for_incoming_call(modem)
    if incoming_number:
        show_incoming_call_on_nextion(incoming_number)
        call_active = True
        while call_active:
            # Listen for Nextion input during incoming call
            if nextion.in_waiting:
                data = nextion.readline().decode('utf-8', errors='ignore').strip()
                print("Nextion input (during incoming call):", data)
                if data == "HANGUP":
                    hangup_call(modem)
                    call_active = False
                elif data == "ANSWER":
                    modem.write(b'ATA\r\n')

                    print("Call accepted.")
            # Listen for remote hangup
            if modem.in_waiting:
                response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
                if "NO CARRIER" in response:
                    print("Call ended by remote party.")
                    modem.reset_input_buffer()
                    modem.reset_output_buffer()
                    modem.write(b"AT+CLIP=1\r")
                    send_nextion_command("page page0")
                    call_active = False
            time.sleep(0.1)

    # 3. Always check for remote hangup (NO CARRIER) outside of call loop
    if modem.in_waiting:
        response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
        if "NO CARRIER" in response:
            print("Call ended by remote party (main loop).")
            modem.reset_input_buffer()
            modem.reset_output_buffer()
            modem.write(b"AT+CLIP=1\r")
            send_nextion_command("page page0")

    time.sleep(0.1)
