import time
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
        # TODO need to use awscli sync method to sync files
        return

    def run(self):
        while True:
            if self.stopped:
                return

            self.scan()
            self.upload()

            # have thread wait for time delta before running scan/upload again
            time.sleep(self.delta)

    def start(self):
        Thread(target=self.run, args=()).start()
        return self

    def stop(self):
        self.stopped = True


if __name__ == '__main__':
    w = Upload()
    w.start()
