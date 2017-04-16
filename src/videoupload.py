import subprocess
import time
from threading import Thread


class Upload():
    def __init__(self, watchdir="/pi/videos", delta=60):
        self.stopped = False
        self.watchdir = watchdir
        self.delta = delta

    def upload(self):
        # run command to sync watchdir folder to aws s3
        subprocess.run(["aws", "s3", "sync", self.watchdir, "s3://sentryvideostorage"])

    def run(self):
        while True:
            if self.stopped:
                return

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
