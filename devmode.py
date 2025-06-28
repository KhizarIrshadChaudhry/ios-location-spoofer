#!/usr/bin/env python3
import asyncio, os, sys, time, threading
from contextlib import asynccontextmanager

from pymobiledevice3.tunneld.server import TunneldRunner
from pymobiledevice3.remote.common import TunnelProtocol

from pymobiledevice3.services.amfi import AmfiService 
from pymobiledevice3.lockdown import create_using_usbmux

import subprocess





from pymobiledevice3.services.mobile_image_mounter import auto_mount



def USBConnection():
    while True:
        try:
            ld = create_using_usbmux() 
            print(f"\n\nEstablished connection with {ld.all_values["ProductName"]}\nUDID: {ld.udid}\nVersion: {ld.all_values["ProductVersion"]}\nTlf.: {ld.all_values["PhoneNumber"]}\nTime Zone: {ld.all_values["TimeZone"]}\nPassword: {ld.all_values["PasswordProtected"]}")
            return ld

        except:
            print(f"Could not establish connection. Trying again...")
            time.sleep(1)

def wait_for_dev_mode(ld, timeout=300):
    print("Waiting for Developer Mode to be enabled...")

    deadline = time.time() + timeout

    while deadline > time.time():
        try:
            #in case of reboot establish connection
            ld = create_using_usbmux()
            status = ld.developer_mode_status

            if status:
                print("✅ Developer Mode is enabled!")
                return ld
            else:
                print("❌ Developer Mode still disabled, retrying...")
        except:
            print(f"⚠️Device rebooting...")

        time.sleep(7)

def start_tunnel():
    '''TunneldRunner.create(
        host="127.0.0.1",
        port=49151,
        protocol=TunnelProtocol.QUIC,
        usb_monitor=True,
        wifi_monitor=True,
        usbmux_monitor=True,
        mobdev2_monitor=True
    )'''

    print("🚀 Launching tunneld subprocess...")
    return subprocess.Popen([
        "sudo", sys.executable, "-m", "pymobiledevice3", "remote", "tunneld"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)



def spoof_location(lat, lon):
    subprocess.run([
        "python", "-m", "pymobiledevice3", 
        "developer", "dvt", "simulate-location", 
        "set", "--", str(lat), str(lon)
    ])

async def main():
    input("🔌 Connect your device and press Enter...")
    ld = USBConnection()

    amfi = AmfiService(ld)
    print("🔓 Revealing Developer Mode toggle...")
    amfi.reveal_developer_mode_option_in_ui()

    print("📲 Go to Settings ▸ Privacy & Security ▸ Developer Mode and toggle it ON.")
    print("⚠️  The device will reboot after you enable it.")
        
    wait_for_dev_mode(ld)

    try:
        print("📦 Mounting Developer Disk Image...")
        await auto_mount(ld)
        print("✅ DDI mounted.")
    except Exception as e:
        if "AlreadyMountedError" in type(e).__name__:
            print("ℹ️ DDI already mounted — continuing.")
        else:
            raise

    
    tunnel_proc = start_tunnel()


    # ✅ Reconnect to see new services exposed by DDI
    ld = create_using_usbmux()

    services = ld.get_value("Services")
    print("Available services:", services)
    spoof_location(55.62530064394984, 12.424319686254321)
    input("Press Enter to reset location...")
    reset_location()

   
def reset_location():
    subprocess.run([
        "python", "-m", "pymobiledevice3", 
        "developer", "dvt", "simulate-location", 
        "clear"
    ])



if __name__ == "__main__":
    asyncio.run(main())







