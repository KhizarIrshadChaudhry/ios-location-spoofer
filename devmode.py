#!/usr/bin/env python3
"""
▸ 1.  create the iOS 17+/RSD tunnel    (sudo required)
▸ 2.  reveal Developer‑Mode in Settings
▸ 3.  block until the user actually flips the switch
▸ 4.  mount the matching Developer Disk Image automatically
"""

import asyncio, os, sys, time
from contextlib import asynccontextmanager

from pymobiledevice3.tunneld.server import TunneldRunner
from pymobiledevice3.remote.common import TunnelProtocol

from pymobiledevice3.services.amfi import AmfiService 
from pymobiledevice3.lockdown import create_using_usbmux


ld = create_using_usbmux() 
udid = ld.udid
amfi = AmfiService(ld)

amfi.reveal_developer_mode_option_in_ui()





