#!/usr/bin/env python3

"""
Klipper FlashMate
A Python tool to simplify the Klipper firmware flashing process.
"""

import os, re, shutil, subprocess, sys

def run(cmd, check=True, capture=False):
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, check=check, text=True,
                                    capture_output=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return ""
    except subprocess.CalledProcessError as e:
        print(f"Error while executing: {cmd}")
        if capture:
            print(e.output)
        if check:
            sys.exit(1)
        return ""

def continue_flash_sequence(selected):
    print("\nSelect flash interface:\n  [1] USB\n  [2] CAN")
    try:
        iface_choice = int(input("\nSelection: "))
    except ValueError:
        print("Invalid input.")
        sys.exit(1)

    if iface_choice == 1:
        serial_dir = "/dev/serial/by-id"
        try:
            entries = sorted(os.listdir(serial_dir))
        except FileNotFoundError:
            print("Directory /dev/serial/by-id/ not found.")
            entries = []
        if not entries:
            print("No serial devices found."); sys.exit(1)
        devices = []
        for i, name in enumerate(entries, start=1):
            full_path = os.path.join(serial_dir, name)
            target = os.readlink(full_path) if os.path.islink(full_path) else "?"
            devices.append((name, target))
            print(f"  [{i}] {name} -> {target}")
        try:
            dev_choice = int(input("\nSelect device number: "))
        except ValueError:
            print("Invalid input."); sys.exit(1)
        if dev_choice < 1 or dev_choice > len(devices):
            print("Invalid selection."); sys.exit(1)
        target_path = os.path.realpath(os.path.join(serial_dir,
                                                    devices[dev_choice-1][0]))
        print("\nBuilding firmware..."); run("make")
        print(f"\nFlashing firmware to {target_path} ...")
        run(f"make flash FLASH_DEVICE={target_path}")

    elif iface_choice == 2:
        print("\nQuerying CAN devices (Klipper CAN IDs)...\n")
        output = run("~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0",
                     check=False, capture=True)
        lines = output.splitlines()
        can_devices = [re.search(r'([0-9a-fA-F]{8,})', l).group(1)
                       for l in lines if re.search(r'([0-9a-fA-F]{8,})', l)]
        if not can_devices:
            print("No CAN devices found."); sys.exit(1)
        print("Detected CAN devices:")
        for i, uid in enumerate(can_devices, start=1):
            print(f"  [{i}] {uid}")
        try:
            can_choice = int(input("\nSelect CAN device number: "))
        except ValueError:
            print("Invalid input."); sys.exit(1)
        if can_choice < 1 or can_choice > len(can_devices):
            print("Invalid selection."); sys.exit(1)
        uid = can_devices[can_choice-1]
        run("make clean"); run("make")
        run(f"~/klippy-env/bin/python3 ~/katapult/scripts/flash_can.py "
            f"-i can0 -f ~/klipper/out/klipper.bin -u {uid}")
    else:
        print("Invalid selection."); sys.exit(1)
    print(f"\nDone. Active configuration: {selected}")

def create_new_config():
    print("Running 'make menuconfig' to create a new configuration...\n")
    if not os.path.isfile("Makefile"):
        print("No Makefile found."); sys.exit(1)
    run("make menuconfig")
    if not os.path.isfile(".config"):
        print("No .config file found."); sys.exit(1)
    name = input("Enter name for new config (suffix after .config_): ").strip()
    if not name: print("No name provided."); sys.exit(1)
    name = re.sub(r"^\.?config_?", "", name)
    newfile = f".config_{name}"
    if os.path.exists(newfile):
        if input(f"{newfile} exists. Overwrite? (y/n): ").lower() not in ("y","yes"):
            print("Aborted."); sys.exit(0)
    shutil.copy(".config", newfile)
    print(f"New configuration saved as {newfile}")
    shutil.copy(newfile, ".config")
    run("make clean")
    continue_flash_sequence(newfile)

def main():
    configs = [f for f in os.listdir(".") if f.startswith(".config_")]
    if not configs:
        print("No configuration files found (.config_*). Creating new.\n")
        create_new_config(); return
    print("Available configurations:\n")
    for i,cfg in enumerate(configs,start=1): print(f"  [{i}] {cfg}")
    choice = input("\nSelect configuration number or type 'new' to create a new one: ").strip().lower()
    if choice == "new": create_new_config(); return
    if not choice.isdigit(): print("Invalid input."); sys.exit(1)
    idx = int(choice)
    if idx < 1 or idx > len(configs): print("Invalid selection."); sys.exit(1)
    selected = configs[idx-1]
    shutil.copy(selected, ".config")
    run("make clean")
    print("\nRunning 'make menuconfig' ...")
    run("make menuconfig")
    continue_flash_sequence(selected)

if __name__ == "__main__":
    main()
