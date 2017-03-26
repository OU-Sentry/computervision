import time
import tinys3
from os import environ
from os import listdir
from os import path
from threading import Thread


class Upload():
    def __init__(self, watchdir=".", delta=60):
        self.stopped = False
        self.watchdir = watchdir
        self.files = {}
        self.delta = delta
        self.pool = tinys3.Pool(environ.get('S3_ACCESS_KEY'),
                                environ.get('S3_SECRET_KEY'),
                                tls=True,
                                default_bucket='sentryvideostorage')

    def scan(self):
        # scan over files in watchdir, update self.files accordingly
        for f in listdir(self.watchdir):
            if path.isfile(f):
                self.files[f] = path.getmtime(f)

    def upload(self):
        # scan over dict, compare time last modified with current time
        # if delta is over n minutes, list of files to upload to S3
        for key in self.files:
            if (time.time() - self.files[key]) >= self.delta:
                print("[INFO] uploading: ", key)
                f = open(key, 'rb')
                self.pool.upload(key, f)

    def run(self):
        while True:
            if self.stopped:
                return

            self.scan()
            self.upload()
            self.stop()

    def start(self):
        Thread(target=self.run, args=()).start()
        return self

    def stop(self):
        self.stopped = True


if __name__ == '__main__':
    w = Upload()
    w.start()
