import urllib.request
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

#Downloads a file as a python file object (bytestream)
def download_object(remote_name):
    try:
        r = urllib.request.urlopen(remote_name)
        if r.getcode() == 200:
            return r.read()
    except Exception as e:
        print("Error downloading file as object ~ {}".format(e))