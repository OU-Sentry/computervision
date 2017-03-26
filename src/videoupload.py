import time
import tinys3
from os import environ
from os import listdir
from os import path


class Watcher():
    def __init__(self, watchdir=".", delta=60):
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

    def checktime(self):
        # scan over dict, compare time last modified with current time
        # if delta is over n minutes, list of files to upload to S3
        for key in self.files:
            if (time.time() - self.files[key]) >= self.delta:
                print("here is one older than a minute ", key)
                f = open(key, 'rb')
                r = self.pool.upload(key, f)
                while r.done() != True:
                    time.sleep(5)
                    print(r)
                    print("waiting on upload")


if __name__ == '__main__':
    w = Watcher()
    w.scan()
    w.checktime()
