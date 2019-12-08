import usb
import struct
import sys
import os
from pathlib import Path


if __name__ == '__main__':

    # Find the switch
    dev = usb.core.find(idVendor=0x057E, idProduct=0x3000)

    # loop until switch is found.
    while (dev is None):
        dev = usb.core.find(idVendor=0x057E, idProduct=0x3000)

    dev.reset()
    dev.set_configuration()
    cfg = dev.get_active_configuration()

    is_out_ep = lambda ep: usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT
    is_in_ep = lambda ep: usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN
    out_ep = usb.util.find_descriptor(cfg[(0,0)], custom_match=is_out_ep)
    in_ep = usb.util.find_descriptor(cfg[(0,0)], custom_match=is_in_ep)

    assert out_ep is not None
    assert in_ep is not None