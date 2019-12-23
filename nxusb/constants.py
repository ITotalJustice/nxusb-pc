
from enum import Enum

SWITCH_VENDOR_ID = 0x057E
SWITCH_PRODUCT_ID = 0x3000
NXUSB_MAGIC = 0x4E58555342

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

	UsbMode_GetWebDownload			= 0x50

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
	UsbReturnCode_FailedTouchFile		= 0x23
	UsbReturnCode_FailedToGetFileSize	= 0x24
	UsbReturnCode_FileNotOpen           = 0x25

	UsbReturnCode_FailedOpenDir         = 0x30
	UsbReturnCode_FailedRenameDir       = 0x31
	UsbReturnCode_FailedDeleteDir       = 0x32
	UsbReturnCode_FailedTouchDir		= 0x33

	UsbReturnCode_Failure				= 0xff

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