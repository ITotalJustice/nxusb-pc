
from enum import Enum

SWITCH_VENDOR_ID = 0x057E
SWITCH_PRODUCT_ID = 0x3000
NXUSB_MAGIC = 0x4E58555342
NXUSB_VERSION_MAJOR = 0
NXUSB_VERSION_MINOR = 0
NXUSB_VERSION_PATCH = 1

class UsbMode(Enum):
	UsbMode_Exit                    	= 0x0
	UsbMode_Ping						= 0x1

	UsbMode_OpenFile                    = 0x10
	UsbMode_OpenFileReadBytes           = 0x11
	UsbMode_OpenFileWrite               = 0x12
	UsbMode_OpenFileWriteBytes          = 0x13
	UsbMode_OpenFileAppend              = 0x14
	UsbMode_OpenFileAppendBytes         = 0x15

	UsbMode_ReadFile                    = 0x20
	UsbMode_WriteFile                   = 0x21
	UsbMode_TouchFile                   = 0x22
	UsbMode_DeleteFile                  = 0x23
	UsbMode_RenameFile                  = 0x24
	UsbMode_GetFileSize                 = 0x25
	UsbMode_GetFileSizeFromPath         = 0x26
	UsbMode_IsFile                      = 0x27
	UsbMode_CloseFile                   = 0x28

	UsbMode_OpenDir                 	= 0x30
	UsbMode_ReadDir                 	= 0x31
	UsbMode_TouchDir                        = 0x32
	UsbMode_DeleteDir                       = 0x33
	UsbMode_GetDirTotal                     = 0x34
	UsbMode_GetDirTotalRecursively          = 0x35
	UsbMode_RenameDir                       = 0x36
	UsbMode_GetDirSize                      = 0x37
	UsbMode_GetDirSizeRecursively           = 0x37
	UsbMode_GetDirSizeFromPath              = 0x37
	UsbMode_GetDirSizeFromPathRecursively   = 0x37
	UsbMode_GetDirTotalFromPath             = 0x38
	UsbMode_GetDirTotalRecursivelyFromPath  = 0x39
	UsbMode_IsDir                           = 0x3A

	UsbMode_OpenDevice              	= 0x40
	UsbMode_ReadDevices             	= 0x41
	UsbMode_GetTotalDevices         	= 0x42

	UsbMode_GetWebDownload				= 0x50

class UsbReturnCode(Enum):
	UsbReturnCode_Success               = 0x0

	UsbReturnCode_PollError             = 0x1
	UsbReturnCode_WrongSizeRead         = 0x2
	UsbReturnCode_WrongSizeWritten      = 0x3
	UsbReturnCode_FailedToInitComms     = 0x4
	UsbReturnCode_WrongHostMagic        = 0x5
	UsbReturnCode_WrongClientMagic      = 0x6
	UsbReturnCode_UnsupportedHosttVer   = 0x7
	UsbReturnCode_UnsupportedCleintVer  = 0x8

	UsbReturnCode_FileNameTooLarge      = 0x10
	UsbReturnCode_EmptyField            = 0x11

	UsbReturnCode_FailedOpenFile        = 0x20
	UsbReturnCode_FailedRenameFile      = 0x21
	UsbReturnCode_FailedDeleteFile      = 0x22
	UsbReturnCode_FailedTouchFile		= 0x23
	UsbReturnCode_FailedGetFileSize		= 0x24
	UsbReturnCode_FileNotOpen           = 0x25
	UsbReturnCode_FailedReadFile        = 0x26
	
	UsbReturnCode_FailedOpenDir         = 0x30
	UsbReturnCode_FailedRenameDir       = 0x31
	UsbReturnCode_FailedTouchDir        = 0x32
	UsbReturnCode_FailedGetDirTotal     = 0x33
	UsbReturnCode_FailedGetDirTotalFromPath = 0x34
	UsbReturnCode_FailedReadDir         = 0x35
	UsbReturnCode_FailedReadDirFromPath = 0x36
	UsbReturnCode_FailedGetDirSize      = 0x37
	UsbReturnCode_FailedGetDirSizeRecursively   = 0x38
	UsbReturnCode_FailedGetDirSizeFromPath      = 0x39
	UsbReturnCode_FailedGetDirSizeRecursivelyFromPath   = 0x3A

	UsbReturnCode_Failure				= 0xff

class USBFileExtentionType(Enum):
	USBFileExtentionType_None   		= 0x0
	USBFileExtentionType_Ignore 		= 0x1

	USBFileExtentionType_Txt    		= 0x10
	USBFileExtentionType_Ini    		= 0x11
	USBFileExtentionType_Html   		= 0x12

	USBFileExtentionType_Zip    		= 0x20
	USBFileExtentionType_7zip   		= 0x21
	USBFileExtentionType_Rar    		= 0x22

	USBFileExtentionType_Mp3    		= 0x30
	USBFileExtentionType_Mp4    		= 0x31
	USBFileExtentionType_Mkv    		= 0x32

	USBFileExtentionType_Nro    		= 0x40
	USBFileExtentionType_Nso    		= 0x41
	
	USBFileExtentionType_Nca    		= 0x50
	USBFileExtentionType_Nsp    		= 0x51
	USBFileExtentionType_Xci    		= 0x52
	USBFileExtentionType_Ncz    		= 0x53
	USBFileExtentionType_Nsz    		= 0x54
	USBFileExtentionType_Xcz    		= 0x55