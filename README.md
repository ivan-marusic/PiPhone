# PiPhone

A DIY phone based on Raspberry Pi 4, SIM7600G-H modem, and Nextion touchscreen, built with Buildroot.

Hardware Documentation

---

## Features

- Custom Buildroot-based Linux system
- Touchscreen dialing interface (Nextion)
- 4G modem for calls, SMS, and GPS (SIM7600G-H)
- Open hardware and software

## Hardware

- Raspberry Pi 4
- SIM7600G-H 4G Shield
- Nextion NX4832T035_011 touchscreen
- Logic level shifter
- See full hardware details here

## Software

- Buildroot config and overlays in `/buildroot`
- Nextion HMI files and scripts in `/software`
- Custom scripts for dialing, AT commands, etc.

## Getting Started

1. **Clone this repo:**
   ```bash
   git clone https://github.com/ivan-marusic/PiPhone.git
   ```
