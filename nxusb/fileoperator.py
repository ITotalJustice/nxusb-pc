from enum import Enum
from .header import *
from .struct_unpacker import unpack_string, unpack_byte, unpack_unsigned_long_long
import os

class fileOperator:
	def __init__(self):
		self.cwd = None
		self.open_file = None
		self.file_mode = None

	def openFile(self, path, mode):
		print("Opening path: {}".format(path_to_open))
		if self.open_file:
			print("Error opening file, there is already an open file - {}".format(self.open_file))
			return UsbReturnCode.UsbReturnCode_FailedOpenFile.value
		if os.path.isfile(path):
			self.open_file = path_to_open
			self.file_mode = mode
			return UsbReturnCode.UsbReturnCode_Success.value
		else:
			print("Error in method OpenFile ~ File does not exits")
			self.open_file = None
			return UsbReturnCode.UsbReturnCode_FailedOpenFile.value

	def closeFile(self):
		if self.open_file:
			self.open_file = None
			self.file_mode = None
			return UsbReturnCode.UsbReturnCode_Success.value
		print("Error, tried to close file but no file was open")
		return UsbReturnCode.UsbReturnCode_FileNotOpen.value

	#Returns true if sucessful
	def writeFile(self, size, offset, data):
		if not self.open_file:
			print("Error, writeFile called but no file is open")
			return UsbReturnCode.UsbReturnCode_FailedOpenFile.value
		print("Writing to file {}".format(self.open_file))
		print("Write size - {}, offset {}".format(size, offset))

		write_file_mode_map = {
			UsbMode.UsbMode_OpenFileWrite.value			: "w",
			UsbMode.UsbMode_OpenFileWriteBytes.value	: "wb",
			UsbMode.UsbMode_OpenFileAppend.value		: "a",
			UsbMode.UsbMode_OpenFileAppendBytes.value	: "ab"
		}

		if not self.file_mode in write_file_mode_map.keys():
			print("Error, writeFile called but file is not open in write mode.")
			return UsbReturnCode.UsbReturnCode_FailedOpenFile.value

		mode = file_mode_map[self.file_mode]

		#If we aren't writing bytes directly, unpack to chars
		if mode in ["w", "a"]:
			data = unpack_string(data, size)

		if mode in ["w", "wb"]:
			with open(self.open_file, mode) as open_file:
				try:
					open_file.seek(offset)
					open_file.write(data)
					print("Wrote {} to file {}".format(data, self.open_file))
					return True
				except Exception as e:
					try:
						print("Error writing to file {} ~ {}".format(path_to_open, e))
					except:
						print("Error writing to file!! {}".format(e))
					return UsbReturnCode.UsbReturnCode_FailedOpenFile.value
		elif mode in ["a", "ab"]:
			with open(self.open_file, mode) as open_file:
				try:
					open_file.write(data)
					print("Appended {} to file {}".format(data, self.open_file))
					return True
				except Exception as e:
					try:
						print("Error appeding to file {} ~ {}".format(path_to_open, e))
					except:
						print("Error appending to file!! {}".format(e))
					return UsbReturnCode.UsbReturnCode_FailedOpenFile.value

	#Returns data if sucessful, Error code if failed
	def readFile(self, size, offset):
		if not self.open_file:
			print("Error, readFile called but no file is open")
			return False
		print("Reading from file {}".format(self.open_file))
		print("Read size - {}, offset {}".format(size, offset))

		read_file_mode_map = {
			UsbMode.UsbMode_OpenFile.value				: "r",
			UsbMode.UsbMode_OpenFileReadBytes.value     : "rb"
		}

		if not self.file_mode in read_file_mode_map.keys():
			print("Error, readFile called but file is not open in read mode.")
			return UsbReturnCode.UsbReturnCode_Failure.value

		mode = file_mode_map[self.file_mode]

		with open(self.open_file, mode) as open_file:
			try:
				open_file.seek(read_offset)
				data = open_file.read(read_size)
				print("Read data {}".format(data))
				return data

			except Exception as e:
				try:
					print("Error reading file {} ~ {}".format(path_to_open, e))
				except:
					print("Error reading file!! {}".format(e))
				return UsbReturnCode.UsbReturnCode_FailedOpenFile.value

	def touchFile(self, path):
		if self.isFileOrDir(path, UsbMode.UsbMode_IsFile.value) is UsbReturnCode.UsbReturnCode_Success.value:
			return UsbReturnCode.UsbReturnCode_Success.value

		if not self.isFileOrDir(path, UsbMode.UsbMode_IsDir.value) is UsbReturnCode.UsbReturnCode_Success.value:
			try:
				with open(path, "w+"):
					return UsbReturnCode.UsbReturnCode_Success.value #If it's not a valid file, make the file and use normal return code
			except:
				pass

		return UsbReturnCode.UsbReturnCode_FailedTouchFile.value

	def touchDir(self, path):
		if self.isFileOrDir(path, UsbMode.UsbMode_IsDir.value) is UsbReturnCode.UsbReturnCode_Success.value:
			return UsbReturnCode.UsbReturnCode_Success.value

		if not self.isFileOrDir(path, UsbMode.UsbMode_IsFile.value) is UsbReturnCode.UsbReturnCode_Success.value:
			try:
				os.mkdir(path)
				return UsbReturnCode.UsbReturnCode_Success.value
			except Exception as e:
				print("Failed to touch dir - {}".format(path))
				return UsbReturnCode.UsbReturnCode_Failure.value
		else:
			return UsbReturnCode.UsbReturnCode_Failure.value

	def deleteFile(self, path):
		print("Deleting file - {}".format(path))
		if not os.path.exists(path):
			return UsbReturnCode.UsbReturnCode_FailedDeleteFile.value
		if os.path.isdir(path):
			return UsbReturnCode.UsbReturnCode_FailedDeleteFile.value
		elif os.path.isfile(path):
			print("Removing {}".format(path))
			os.remove(path)
			return UsbReturnCode.UsbReturnCode_Success.value
		else:
			raise


	def renameFile(self, curr_name, new_name):
		if not os.path.exists(curr_name) or os.path.exists(new_name):
			return UsbReturnCode.UsbReturnCode_FailedRenameFile.value
		try:
			shutil.move(curr_name, new_name)
			print("Moved {} to {}".format(curr_name, new_name))
			return UsbReturnCode.UsbReturnCode_Success.value
		except Exception as e:
			print("Error renaming file ~ {}".format(e))
			return UsbReturnCode.UsbReturnCode_FailedRenameFile.value

	# Usb Method Helpers
	def isFileOrDir(self, path, mode):
		if not os.path.exists(path):
			return UsbReturnCode.UsbReturnCode_Failure.value

		if mode is UsbMode.Usbmode_pathExists.value:
			return UsbReturnCode.UsbReturnCode_Success.value

		if os.path.isdir(path):
			if mode is UsbMode.Usbmode_IsDir.value:
				return UsbReturnCode.UsbReturnCode_Success.value
			return UsbReturnCode.UsbReturnCode_Failure.value
		elif os.path.isfile(path):
			if mode is UsbMode.Usbmode_IsFile.value:
				return UsbReturnCode.UsbReturnCode_Success.value
			return UsbReturnCode.UsbReturnCode_Failure.value
		else:
			raise fileError

	#Works
	def deleteDir(self, path, recursive = False):
		try:
			print("Verifying dir validity.")
			status = self.isFileOrDir(path, UsbMode.Usbmode_isDir.value)
			if not status is UsbReturnCode.UsbReturnCode_Success.value:
				return status

			if recursive:
				shutil.rmtree(path) #Removes dir recursively
			else:
				os.rmdir(path) #Removes dir non-recursively
			return UsbReturnCode.UsbReturnCode_Success.value

		except Exception as e:
			try:
				print("Failed to delete dir [recursive: {}] {} ~ {}".format(recursive, path, e))
			except:
				print("Failed to delete dir [recursive: {}]! ~ {}".format(recursive, e))
			return UsbReturnCode.UsbReturnCode_FailedDeleteDir.value