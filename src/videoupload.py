import time
from os import listdir
from os import path


class Watcher():
    def __init__(self, watchdir="."):
        self.watchdir = watchdir
        self.files = {}

    def scan(self):
        # scan over files in watchdir, update self.files accordingly
        for f in listdir(self.watchdir):
            if path.isfile(f):
                self.files[f] = path.getmtime(f)

    def checktime(self):
        # scan over dict, compare time last modified with current time
        # if delta is over n minutes, list of files to upload to S3
        for key in self.files:
            print(self.files[key])


if __name__ == '__main__':
    w = Watcher()
    w.scan()
    w.checktime()
