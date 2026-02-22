The PiPhone is a DIY mobile phone built using:

- **Raspberry Pi 4** as the main computing unit
- **SIM7600G-H 4G modem** for cellular connectivity
- **Nextion NX4832T035_011 touchscreen** for user interface
- **Logic level shifter** to safely connect 5V Nextion UART to 3.3V Pi UART
- **Power supply** (5V 3A recommended)
- Optional: **speaker**, **microphone**

## Components List (BOM)

| Component                  | Model/Spec                     | Notes                                      |
|---------------------------|--------------------------------|--------------------------------------------|
| Raspberry Pi              | Pi 4 Model B (2GB)             | Main board                                 |
| 4G Modem                  | SIM7600G-H                     | USB or UART connection                     |
| Touchscreen               | Nextion NX4832T035_011         | 3.5" HMI display                           |
| Logic Level Shifter       | TXB0104 or similar             | For UART voltage compatibility             |
| MicroSD Card              | 32GB                           | For Buildroot image                        |
| Power Supply              | 5V 3A USB-C                    | Stable power for Pi and modem              |
| Jumper Wires              | Male-to-female                 | For UART and power connections             |
| Optional: Speaker/Mic     | Analog or USB                  | For audio I/O                              |

## Wiring Diagram

| Connection                | From (Device)         | To (Device)              | Notes                          |
|--------------------------|-----------------------|--------------------------|--------------------------------|
| UART TX                  | Nextion TX            | Pi GPIO15 (RXD)          | Use logic level shifter        |
| UART RX                  | Nextion RX            | Pi GPIO14 (TXD)          | Use logic level shifter        |
| GND                      | Nextion GND           | Pi GND                   | Common ground                  |
| 5V Power                 | Nextion VCC           | Pi 5V (Pin 2 or 4)       | Ensure power stability         |
| USB                      | SIM7600G-H USB        | Pi USB Port              | For modem communication        |
| UART (optional)          | SIM7600G-H TX/RX      | Pi GPIO (via shifter)    | Only if using UART instead of USB |

> **Tip:** Use `minicom` or `screen` to test UART communication with both the Nextion and SIM7600G-H.

## Testing Hardware

1. **Power on the Pi** with the SIM7600G-H and Nextion connected.
2. **Check USB modem**:
   ```bash
   ls /dev/ttyUSB*
   ```
