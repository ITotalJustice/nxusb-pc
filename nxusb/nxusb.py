import usb
import struct
import sys
import os
import shutil
from timeit import default_timer as timer
from .header import *
from .webhandler import download_object
from .fileoperator import fileOperator
from .struct_unpacker import unpack_string, unpack_byte, unpack_unsigned_long_long

class usb_tool:
	def __init__(self):
		self.dev = None
		self.out_ep = None
		self.in_ep = None
		self.is_connected = False
		self.open_file = None
		self.cwd = None
		self.fileOperator = fileOperator()

		self.UsbModeMap = {
			UsbMode.UsbMode_Exit.value : self.exit,
			UsbMode.UsbMode_Ping.value : self.ping,

			UsbMode.UsbMode_OpenFile.value : self.OpenFile,
			UsbMode.UsbMode_OpenFileReadBytes.value : self.OpenFileReadBytes,
			UsbMode.UsbMode_OpenFileWrite.value : self.OpenFileWrite,
			UsbMode.UsbMode_OpenFileWriteBytes.value : self.OpenFileWriteBytes,
			UsbMode.UsbMode_OpenFileAppend.value : self.OpenFileAppend,
			UsbMode.UsbMode_OpenFileAppendBytes.value : self.OpenFileAppendBytes,

			UsbMode.UsbMode_ReadFile.value : self.ReadFile,
			UsbMode.UsbMode_WriteFile.value : self.WriteFile,
			UsbMode.UsbMode_TouchFile.value : self.TouchFile,
			UsbMode.UsbMode_DeleteFile.value : self.DeleteFile,
			UsbMode.UsbMode_RenameFile.value : self.RenameFile,
			UsbMode.UsbMode_GetFileSize.value : self.GetFileSize,
			UsbMode.UsbMode_GetFileSizeFromPath.value : self.GetFileSizeFromPath,
			UsbMode.UsbMode_IsFile.value : self.isFile,
			UsbMode.UsbMode_CloseFile.value : self.CloseFile,

			UsbMode.UsbMode_OpenDir.value : self.OpenDir,
			UsbMode.UsbMode_ReadDir.value : self.ReadDir,
			UsbMode.UsbMode_TouchDir.value : self.TouchDir,
			UsbMode.UsbMode_DeleteDir.value : self.DeleteDir,
			# UsbMode.UsbMode_DeleteDirRecursively.value : self.DeleteDirRecursively,
			UsbMode.UsbMode_GetDirTotal.value : self.GetDirTotal,
			UsbMode.UsbMode_GetDirTotalRecursively.value : self.GetDirTotalRecursively,
			UsbMode.UsbMode_RenameDir.value : self.RenameDir,                   
		    UsbMode.UsbMode_GetDirSize.value :  self.GetDirSize,
		    UsbMode.UsbMode_GetDirSizeRecursively.value :  self.GetDirSize,
		    UsbMode.UsbMode_GetDirSizeFromPath.value :  self.GetDirSize,
		    UsbMode.UsbMode_GetDirSizeFromPathRecursively.value :  self.GetDirSize,
		    UsbMode.UsbMode_GetDirTotalFromPath.value : self.GetDirSize,
		    UsbMode.UsbMode_GetDirTotalRecursivelyFromPath.value : self.GetDirSize,
		    UsbMode.UsbMode_IsDir.value : self.isDir,

			UsbMode.UsbMode_OpenDevice.value : self.OpenDevice,
			UsbMode.UsbMode_ReadDevices.value : self.ReadDevices,
			UsbMode.UsbMode_GetTotalDevices.value : self.GetTotalDevices,
			UsbMode.UsbMode_GetWebDownload.value : self.GetWebDownload,
		}

	def OpenFile(self, size, io_in):
		return self.fileOperator.openFile(unpack_string(io_in, size), UsbMode.UsbMode_OpenFile.value)
	def OpenFileReadBytes(self, size, io_in):
		return self.fileOperator.openFile(unpack_string(io_in, size), UsbMode.UsbMode_OpenFileReadBytes.value)
	def OpenFileWrite(self, size, io_in):
		return self.fileOperator.openFile(unpack_string(io_in, size), UsbMode.UsbMode_OpenFileWrite.value)
	def OpenFileWriteBytes(self, size, io_in):
		return self.fileOperator.openFile(unpack_string(io_in, size), UsbMode.UsbMode_OpenFileWriteBytes.value)
	def OpenFileAppend(self, size, io_in):
		return self.fileOperator.openFile(unpack_string(io_in, size), UsbMode.UsbMode_OpenFileAppend.value)
	def OpenFileAppendBytes(self, size, io_in):
		return self.fileOperator.openFile(unpack_string(io_in, size), UsbMode.UsbMode_OpenFileAppendBytes.value)

	def GetFileSizeFromPath(self, size, io_in):
		raise notImplemented
	def GetDirSize(self, size, io_in):
		raise notImplemented
	def GetDirTotal(self, size, io_in):
		raise notImplemented
	def GetDirTotalRecursively(self, size, io_in):
		raise notImplemented
	def RenameDir(self, size, io_in):
		raise notImplemented
	def OpenDevice(self, size, io_in):
		raise notImplemented
	def ReadDevices(self, size, io_in):
		raise notImplemented
	def GetTotalDevices(self, size, io_in):
		raise notImplemented

	def addUSBcommand(self, value, callback):
		if not value in self.UsbModeMap.keys():
			self.UsbModeMap[value] = callback
		else:
			print("Error adding usb command, value overlap")
			raise overlapError

	def addUSBcommands(self, command_list):
		for value, callback in command_list:
			self.addUSBcommand(value, callback)

	#Tested
	def init(self):
		print("Starting Switch connection")
		if not self.wait_for_switch_to_connect(silent = True): #Populates self.dev when the switch is connected
			rint("Can't init switch connection")
			return False
		try:
			dev = self.dev
			dev.reset()
			dev.set_configuration()
			cfg = dev.get_active_configuration()

			ep = self.get_endpoints(cfg)
			out_ep = ep[1]
			in_ep = ep[0]

			assert out_ep is not None
			assert in_ep is not None

			self.out_ep = out_ep
			self.in_ep = in_ep

			if not self.attempt_handshake():
				print("Handshake failed")
				return False

			self.is_connected = True
			return True
		except Exception as e:
			print("Error: Failed to init switch connection ~ {}".format(e))
			return None

	#-------------------------------
	#Handshake struct:
	#The first 8 bytes are magic [0x4E58555342]
	#Then 3 bytes for the version [Macro, micro, major]
	#Then 5 bytes of padding
	#----------------------------
	#Handshake protocol
	#The switch writes a handshake struct of length 0x10
	#The pc writes a success code
	#The pc writes a handshake struct
	def attempt_handshake(self):
		try:
			io_in = self.in_ep.read(0x10, timeout=0)
			magic = unpack_unsigned_long_long(io_in[0x0:0x8])
			if not magic == NXUSB_MAGIC:
				print("Invalid USB Magic")
				return False

			try:
				macro = unpack_byte(io_in[0x8:0x9])
				minor = unpack_byte(io_in[0x9:0xA])
				major = unpack_byte(io_in[0xA:0xB])
			except Exception as e:
				print("Handshake unpack error: {}".format(e))
				return False
			self.writeUSBReturnSuccess()

			outstruct = struct.pack("<Q3B5x", NXUSB_MAGIC, NXUSB_VERSION_MAJOR, NXUSB_VERSION_MINOR, NXUSB_VERSION_PATCH)
			self.writeUSB(outstruct)

			print("Handshake successful, switch client version {}.{}.{}".format(major, minor, macro))
			return True

		except Exception as e:
			print("Handshake error ~ {}".format(e))
			return False

	#Call when app is ready
	def mainloop(self):
		while True:
			self.mode_poll()

#Utility functions
	# Find a ready switch, returns usb device
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

	#Pass device config, get endpoints in tuple
	def get_endpoints(self, cfg):
		print("Getting endpoints")
		print("==============================================================")

		in_ep = _get_in_endpoint(cfg)
		print("In:")
		print(in_ep)

		out_ep = _get_out_endpoint(cfg)
		print("Out:")
		print(out_ep)

		print("==============================================================")
		assert in_ep is not None
		assert out_ep is not None
		return(in_ep, out_ep)

	#Finished
	def exit(self, size=None, data = None):
		print("Received USB exit command...")
		self._exit()

	def _exit(self):
		sys.exit("Exiting...")

#Read and write functions
	def readUSB(self, length, timeout = 0):
		if not length:
			return False
		try:
			data = self.in_ep.read(length, timeout = timeout)
			print("Received data - {}".format(data))
			return data
		except Exception as e:
			print("Error reading USB ~ {}".format(e))
		
	def readUSBRaw(self, length, timeout = 0):
		return self.in_ep.read(length, timeout = timeout).tobytes()

	#Returns True if successful
	def writeUSB(self, outstruct, timeout = 1000):
		if not outstruct:
			print("Empty struct passed to writeUSB")
			return False
		try:
			self.dev.write(endpoint = self.out_ep, data = outstruct, timeout = timeout)
			return True
		except Exception as e:
			print("Error writing to USB ~ {}".format(e))

	#Shortcut to write usb retrun codes
	#Returns True if sucessful
	def writeUSBReturnCode(self, code):
		if code is None:
			print("Error writing USB return code. Return code is None.")
			raise usbError
		outstruct = struct.pack("<l", code)
		print("Writing USBReturnCode {}".format(UsbReturnCode(code)))
		return self.writeUSB(outstruct)

	#Shortcut to write usb success code
	#Returns True if sucessful
	def writeUSBReturnSuccess(self):
		return self.writeUSBReturnCode(UsbReturnCode.UsbReturnCode_Success.value)

		#Writes a file given it's path
	def writeUSBfile(file_path, range_size, range_offset):
		with open(file_path) as f:
			return self._writeUSBfile(f, range_size, range_offset)

		#Writes a file object to USB in 1MiB chunks
	def _writeUSBfile(file_object, range_size, range_offset):
		try:
			f = file_object
			f.seek(range_offset)

			curr_off = 0x0
			end_off = range_size
			read_size = 0x100000 # 1MiB

			while curr_off < end_off:
				if curr_off + read_size >= end_off:
					read_size = end_off - curr_off

				buf = f.read(read_size)
				if not self.writeUSB(buf):
					raise usbError
				curr_off += read_size
				print("reading {} - {}".format(curr_off, end_off))

			return True
		except Exception as e:
			print("Error writing file to usb range_size: {}, range_offset {}".format(range_size, range_offset))
			return False

#Usb Commands
	#Test ping
	def ping(self, size, io_in):
		return UsbReturnCode.UsbReturnCode_Success.value

	def pathExist(self, size, io_in):
		path_to_open = unpack_string(io_in, size)
		return self.fileOperator.isFileOrDir(path_to_open, UsbMode.Usbmode_pathExists.value)

	def isFile(self, size, io_in):
		path_to_open = unpack_string(io_in, size)
		return self.fileOperator.isFileOrDir(path_to_open, UsbMode.Usbmode_isFile.value)

	def isDir(self, size, io_in):
		path_to_open = unpack_string(io_in, size)
		return self.fileOperator.isFileOrDir(path_to_open, UsbMode.Usbmode_isDir.value)

	#Not tested
	def ReadFile(self, size, io_in):
		try:
			read_size = unpack_unsigned_long_long(io_in[0x0:0x8])
			read_offset = unpack_unsigned_long_long(io_in[0x8:0x10])
			print("Read size {}".format(read_size))
			print("Read read_offset {}".format(read_offset))
		except Exception as e:
			print("Exception unpacking ReadFile struct ~ {}".format(e))

		data = self.fileOperator.readFile(read_size, read_offset)
		if data in [UsbReturnCode.UsbReturnCode_Failure.value, UsbReturnCode.UsbReturnCode_FailedOpenFile.value]:
			return data
		else:
			try:
				if not self.writeUSB(data):
					print("error writing contents to usb")
					return UsbReturnCode.UsbReturnCode_FailedOpenFile.value
				print("successfully wrote contents to usb")
				return -1
			except Exception as e:
				print("Failed to write file contents to usb ~ {}".format(e))
				return UsbReturnCode.UsbReturnCode_FailedOpenFile.value

	def WriteFile(self, size, io_in):
		write_size = unpack_unsigned_long_long(io_in[0x0:0x8])
		write_offset = unpack_unsigned_long_long(io_in[0x8:0x10])
		data_in = self.readUSB(write_size)
		data_in = unpack_string(data_in, write_size)

		return self.fileOperator.writeFile(write_size, write_offset, data_in)

	def CloseFile(self, size, io_in):
		return self.fileOperator.closeFile()

	def TouchFile(self, size, io_in):
		path_to_open = unpack_string(io_in, size)
		return self.fileOperator.touchFile(path_to_open)

	def DeleteFile(self, size, io_in):
		path_to_open = unpack_string(io_in, size)
		return self.fileOperator.deleteFile(path_to_open)

	def RenameFile(self, size, io_in):
		try:
			size_1 = unpack_unsigned_long_long(io_in[0x0:0x8])
			size_2 = unpack_unsigned_long_long(io_in[0x8:0x10])
			print("Size_1: {}, Size_2: {}".format(size_1, size_2))
			data_in = self.readUSB(size_1)
			curr_name = unpack_string(data_in, size_1)
			data_in = self.readUSB(size_2)
			new_name = unpack_string(data_in, size_2)
			print("Filename_1: {}, Filename_2: {}".format(curr_name, new_name))
		except Exception as e:
			print("Error unpacking file rename strings / sizes ~ {}".format(e))
			return UsbReturnCode.UsbReturnCode_FailedRenameFile.value

		return self.fileOperator.renameFile(curr_name, new_name)

	#Works
	def GetFileSize(self, size, io_in):
		path_to_open = unpack_string(io_in, size)
		if not os.path.exists(path_to_open) or os.path.isdir(path_to_open):
				return 0x0

		if os.path.isfile(path_to_open):
			return os.path.getsize(path_to_open)
		else:
			raise fileError

		print("Path: {}".format(path_to_open))
		filesize = do_get_file_size(path_to_open)
		outstruct = struct.pack('<Q', filesize)
		self.writeUSB(outstruct)
		return -1 #Prevents the sending of the usb return code

	def OpenDir(self, size, io_in):
		try:
			path_to_open = unpack_string(size, io_in)

			if not os.path.exists(path_to_open):
				self.cwd = None
				return UsbReturnCode.UsbReturnCode_FailedOpenDir.value
			if os.path.isdir(path_to_open):
				self.cwd = path_to_open
				return UsbReturnCode.UsbReturnCode_Success.value
			elif os.path.isfile(path_to_open):
				self.cwd = None
				return UsbReturnCode.UsbReturnCode_FailedOpenDir.value
			else:
				self.cwd = None
				raise fileError
		except Exception as e:
			print("Error: failed to change working dir ~ {}".format(e))
			return UsbReturnCode.UsbReturnCode_FailedOpenDir.value
		
	def ChangeDir(self, size, io_in):
		try:
			path_to_open = unpack_string(size, io_in)

			if not os.path.exists(path_to_open):
				return UsbReturnCode.UsbReturnCode_FailedOpenDir.value
			if os.path.isdir(path_to_open):
				os.chdir(path)
			elif os.path.isfile(path_to_open):
				return UsbReturnCode.UsbReturnCode_FailedOpenDir.value
			else:
				raise
		except Exception as e:
			try:
				print("Error: failed to open dir {} ~ {}".format(path_to_open, e))
			except:
				print("Error: failed to open dir! ~ {}".format(e))
			return UsbReturnCode.UsbReturnCode_FailedOpenDir.value

	def ReadDir(self, size, io_in):
		print("Testing if dir exists")
		status = self.isDir(size, io_in)
		if not status is UsbReturnCode.UsbReturnCode_Success:
			return status
		
		path_to_open = unpack_string(io_in, size)

		dirs = os.listdir(path_to_open)

		out_buffer = bytearray(0x1000)
			
		offset = 0x0
		struct.pack_into("<Q", out_buffer, offset, len(dirs))
		offset += 0x8

		if len(dirs):
			for x in range(0, len(dirs)):
				struct.pack_into("<Q", out_buffer, offset, lens[x])
				offset += 0x8

			for x in range(0, len(dirs)):
				struct.pack_into("<{}s".format(len(dirs)), out_buffer, offset, dir_list[x])
			offset += len(dir_list[x])

		out_buffer = out_buffer[0:offset]
		self.writeUSB(struct.pack('<Q',offset)) #Write unsigned_long_long length of data 
		self.writeUSB(out_buffer) #Write data

		# Unpack Process
		# list_len = unpack_unsigned_long_long(io_in[0x0:0x8])
		# offset = 0x8
		# lens = []
		# for x in range(0, list_len):
		# 	lens.append(unpack_unsigned_long_long(io_in[offset:offset+0x8]))
		# 	offset += 0x8
		# dirs = []
		# for x in range(0, list_len):
		# 	dirs.append(unpack_string(io_in[offset:offset+lens[x]]))
		# 	offset + lens[x]

		# struct {
		# Num_entries
		# Len_entry_1
		# Len_entry_2
		# ...
		# len_entry_NUM_ENTRIES
		# entry_1
		# entry_2
		# entry_3
		# ...
		# }	

	#Works
	def DeleteDir(self, size, io_in):
		return self.fileOperator.DeleteDir(size, io_in, recursive = False)

	#Not written yet switch-side, probably works though
	def DeleteDirRecursively(self, size, io_in):
		return self._DeleteDir(size, io_in, recursive = True)

	def _DeleteDir(self, size, io_in, recursive):
		path = unpack_string(io_in, size)
		print("Deleting dir {}".format(path_to_open))
		return self.fileOperator.DeleteDir(path, recursive = recursive)

	def TouchDir(self, size, io_in):
		path_to_open = unpack_string(io_in, size)
		print("Path: {}".format(path_to_open))
		return self.fileOperator.touchDir(path_to_open)

	def GetWebDownload(self, size, io_in):
		raise notImplemented

		url = unpack_string(io_in, size)
		try:
			f = download_object(url)
			size = len(f)
		except Exception as e:
			try:
				print("Error downloading file from url {} ~ {}".format(url, e))
			except:
				print("Error downloading file ~ {}".format(url, e))
			return USBReturnCode.UsbReturnCode_Failure.value

		#Write length so the switch can allocate memory to receive it
		outstruct = struct.pack("<Q", size)
		self.writeUSB(outstruct)

		response = self.readUSB(0x4)
		status = struct.unpack("<l", response)

		if status == USBReturnCode.UsbReturnCode_Success.value:
			status = self._writeUSBfile(f, size, 0)

		return status

	#returns mode if mode was found
	def mode_poll(self):
		# try:
		print("\n\nAwaiting command...")
		try:
			io_in = self.readUSB(0x10)
		except usb.core.USBError as e:
			print("Error polling USB (Device disconnnected?) reinitializing...")
			return
		
		if not io_in:
			print("No command received.")
			raise usbError

		try:
			mode = unpack_byte(io_in[0x0:0x1])
			padding = struct.unpack('<7?', io_in[0x1:0x8])[0]
			size = unpack_unsigned_long_long(io_in[0x8:0x10])
			print("Mode: {}, Size: {}".format(mode, size))
			print("Received Command {}".format(UsbMode(mode)))
		except Exception as e:
			print("Error unpacking command struct ~ {}".format(e))
			return

		try:
			function = self.UsbModeMap[mode]
		except Exception as e:
			try:
				print("Error selecting mode: {} ~ {}".format(mode,e))
			except:
				print("Error selecting mode! {}".format(e))
			return

		data = self.readUSB(size)
		if size > 0 and not data:
			result = USBReturnCode.UsbReturnCode_WrongSizeRead.value
		else:
			result = function(size, data)
		if not result == -1:
			self.writeUSBReturnCode(result)

#Endpoint functions
def _get_endpoint(direction, cfg):
	is_ep = lambda ep: usb.util.endpoint_direction(ep.bEndpointAddress) == direction
	return usb.util.find_descriptor(cfg[(0,0)], custom_match = is_ep)

def _get_out_endpoint(cfg):
	return _get_endpoint(usb.util.ENDPOINT_OUT, cfg)

def _get_in_endpoint(cfg):
	return _get_endpoint(usb.util.ENDPOINT_IN, cfg)