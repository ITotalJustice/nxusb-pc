import usb
import struct
import sys
import os
from pathlib import Path
from timeit import default_timer as timer

SWITCH_VENDOR_ID = 0x057E
SWITCH_PRODUCT_ID = 0x3000

class usb_tool:
	def __init__(self):
		self.dev = None
		self.out_ep = None
		self.in_ep = None

	def init(self):
		print("Starting Switch connection")
		if self.wait_for_switch_to_connect(silent = True):
			try:
				dev = self.dev
				dev.reset()
				dev.set_configuration()
				cfg = dev.get_active_configuration()

				is_out_ep = lambda ep: usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT
				is_in_ep = lambda ep: usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN
				out_ep = usb.util.find_descriptor(cfg[(0,0)], custom_match=is_out_ep)
				in_ep = usb.util.find_descriptor(cfg[(0,0)], custom_match=is_in_ep)

				assert out_ep is not None
				assert in_ep is not None

				self.out_ep = out_ep
				self.in_ep = in_ep
			except Exception as e:
				print("Error: Failed to init Switch connection ~ {}".format(e))
		else:
			print("Can't init switch connection")

	# Find the switch
	def find_switch(self, silent = False):
		if not silent:
			print("Searcing for Nintendo Switch (VendorID: {}, ProductID: {}".format(str(SWITCH_VENDOR_ID), str(SWITCH_PRODUCT_ID)))
		return usb.core.find(idVendor=SWITCH_VENDOR_ID, idProduct=SWITCH_PRODUCT_ID)

	# Wait for the switch to connect, set a timeout or wait indefinitely
	# Silent mutes the find function but doesn't mute printouts
	# True if found | False if not found
	def wait_for_switch_to_connect(self, timeout = None, silent = False):
		dev = None
		# loop until switch is found.
		starttime = timer()
		while (dev is None):
			if timeout:
				if (timer() > (starttime + timeout)):
					print("Switch connection timeout exceeded")
					break
			dev = self.find_switch(silent = silent)
		self.dev = dev
		if dev:
			print("Found switch")
			return True
		else:
			print("Failed to find switch")
			return False
		