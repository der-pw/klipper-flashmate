# Klipper FlashMate

**A Python tool to simplify the Klipper firmware flashing process.**

Klipper FlashMate helps you manage multiple firmware configurations for different MCUs, build them cleanly, and flash them quickly via **USB** or **CAN** — all from one interactive command-line tool.

---

## Features

- Manage multiple `.config_*` firmware configurations
- Create new configurations using `make menuconfig`
- Automatically copy, clean, and prepare build environments
- Flash firmware via USB or CAN (with easy device selection)
- Consistent, menu-driven workflow for all MCUs

---

## Requirements

Before using **Klipper FlashMate**, make sure you have:

- A working **Klipper build environment**  
  (e.g. `make`, `menuconfig`, and your Klipper source checked out)
- **Python 3.6 or newer**
- The following tools available in your shell:
  - `make`
  - `python` / `python3`
  - `~/klippy-env` (used by Klipper for CAN communication)
  - [Katapult bootloader](https://github.com/Arksine/katapult) installed on all MCUs  
    (both USB and CAN devices must use the Katapult bootloader)

---

## Installation

Download **Klipper FlashMate** directly into your Klipper folder:

```bash
cd ~/klipper
wget https://raw.githubusercontent.com/der-pw/klipper-flashmate/main/klipper-flashmate.py
chmod +x klipper-flashmate.py
```

## Usage
Run the tool directly:
```./klipper-flashmate.py```

Typical workflow
Choose an existing configuration or type new to create a new one.
If creating a new config:
make menuconfig will open.
When finished, enter a name (e.g. myboard).
The config will be saved as .config_myboard.
Klipper FlashMate will:
- Copy the configuration to .config
- Run make clean
- Build and flash firmware via USB or CAN

## Example

=== Klipper FlashMate ===
```
Available configurations:
  [1] .config_stm32f4
  [2] .config_rp2040

Select configuration number or type 'new' to create a new one: new
Running 'make menuconfig' to create a new configuration...

Enter a name for the new config file (suffix after .config_): octopus
New configuration saved as: .config_octopus

Copying .config_octopus to .config ...
Running 'make clean' ...

Select flash interface:
  [1] USB
  [2] CAN
Selection: 1

Listing available USB devices:
  [1] usb-Klipper_STM32F446xx-if00 -> ../../ttyACM0

Select device number: 1
Building firmware...
Flashing firmware to /dev/ttyACM0 ...
Done. Active configuration: .config_octopus
```

## Notes
- All MCUs (USB and CAN) must run the Katapult bootloader.
- For CAN-based flashing, the script uses:
  - ~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
  - ~/klippy-env/bin/python3 ~/katapult/scripts/flash_can.py
- For USB-Based flashing, the script uses
  - make flash FLASH_DEVICE=/dev/ttyACMxx

## Author
Klipper FlashMate was created to streamline the firmware workflow for Klipper users who manage multiple microcontrollers and need a fast, consistent way to build and flash firmware.
