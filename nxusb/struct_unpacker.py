import struct
from .header import unpackError

def unpack_string(data, size = None, silent = False):
	try:
		if size:
			data = struct.unpack('<{}s'.format(size), data[0x0:size])[0]
		else:
			data = struct.unpack('<{}s'.format(len(data)), data)[0]
		if not silent:
			print("Unpacked string {}".format(data))
		return data
	except Exception as e:
		print("Error unpacking data to string.\n     Data: {}\n     Size: {}\n     Error: {}".format(data, size, e))
		raise unpackError

def unpack_unsigned_long_long(data):
	try:
		return struct.unpack('<Q', data)[0]
	except Exception as e:
		print("Error unpacking data to unsigned long long.\n     Data: {}\n     Error: {}".format(data, e))
		raise unpackError

def unpack_byte(data):
	return struct.unpack('<B', data)[0]