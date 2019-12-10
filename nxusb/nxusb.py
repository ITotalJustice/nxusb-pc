import usb
import struct
import sys
import os
import io
from pathlib import Path
from timeit import default_timer as timer
from enum import Enum

SWITCH_VENDOR_ID = 0x057E
SWITCH_PRODUCT_ID = 0x3000


class UsbMode(Enum):
	UsbMode_Exit                    = 0x0
	UsbMode_Ping                    = 0x1

	UsbMode_OpenFile                = 0x10
	UsbMode_ReadFile                = 0x11
	UsbMode_WriteFile               = 0x12
	UsbMode_TouchFile               = 0x13
	UsbMode_DeleteFile              = 0x14
	UsbMode_RenameFile              = 0x15
	UsbMode_GetFileSize             = 0x16
	UsbMode_CloseFile               = 0x20

	UsbMode_OpenDir                 = 0x30
	UsbMode_ReadDir                 = 0x31
	UsbMode_DeleteDir               = 0x32
	UsbMode_DeleteDirRecursively    = 0x33
	UsbMode_GetDirTotal             = 0x34
	UsbMode_GetDirTotalRecursively  = 0x35
	UsbMode_RenameDir               = 0x36
	UsbMode_TouchDir                = 0x37

	UsbMode_OpenDevice              = 0x40
	UsbMode_ReadDevices             = 0x41
	UsbMode_GetTotalDevices         = 0x42

class UsbReturnCode(Enum):
	UsbReturnCode_Success               = 0x0

	UsbReturnCode_PollError             = 0x1
	UsbReturnCode_WrongSizeRead         = 0x2
	UsbReturnCode_WrongSizeWritten      = 0x3

	UsbReturnCode_FileNameTooLarge      = 0x10
	UsbReturnCode_EmptyField            = 0x11

	UsbReturnCode_FailedOpenFile        = 0x20
	UsbReturnCode_FailedRenameFile      = 0x21
	UsbReturnCode_FailedDeleteFile      = 0x22

	UsbReturnCode_FailedOpenDir         = 0x30
	UsbReturnCode_FailedRenameDir       = 0x31
	UsbReturnCode_FailedDeleteDir       = 0x32

class USBFileExtentionType(Enum):
    USBFileExtentionType_None   = 0x0
    USBFileExtentionType_Ignore = 0x1

    USBFileExtentionType_Txt    = 0x10
    USBFileExtentionType_Ini    = 0x11
    USBFileExtentionType_Html   = 0x12

    USBFileExtentionType_Zip    = 0x20
    USBFileExtentionType_7zip   = 0x21
    USBFileExtentionType_Rar    = 0x22

    USBFileExtentionType_Mp3    = 0x30
    USBFileExtentionType_Mp4    = 0x31
    USBFileExtentionType_Mkv    = 0x32

    USBFileExtentionType_Nro    = 0x40
    USBFileExtentionType_Nso    = 0x41
	
    USBFileExtentionType_Nca    = 0x50
    USBFileExtentionType_Nsp    = 0x51
    USBFileExtentionType_Xci    = 0x52
    USBFileExtentionType_Ncz    = 0x53
    USBFileExtentionType_Nsz    = 0x54
    USBFileExtentionType_Xcz    = 0x55

class usb_tool:
	def __init__(self):
		self.dev = None
		self.out_ep = None
		self.in_ep = None
		self.is_connected = False

		self.read_buf = io.BytesIO()
		self.write_buf = io.BytesIO()

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
				self.is_connected = True
			except Exception as e:
				print("Error: Failed to init Switch connection ~ {}".format(e))
		else:
			print("Can't init switch connection")

	def clear(self):
		self.read_buf = io.BytesIO()
		self.write_buf = io.BytesIO()

	def test(self):
		ping_in = self.in_ep.read(0x10, timeout=0)
		try:
			mode = struct.unpack('<Q', ping_in[0:8])[0]
			size = struct.unpack('<Q', ping_in[0x8:0x10])[0]

			if mode and size:
				print("Mode: {}, Size: {}".format(mode, size))
		except Exception as e:
			print("Error in test {}".format(e))

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