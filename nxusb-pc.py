from nxusb import usbClient

if __name__ == '__main__':
    usbClient.init()
    while True:
        usbClient.test()