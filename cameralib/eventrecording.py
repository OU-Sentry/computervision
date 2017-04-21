from collections import deque
from threading import Thread
from queue import Queue
import time
import cv2


class EventDetection:
    def __init__(self, bufsize=64, timeout=1.0):
        self.bufsize = bufsize
        self.timeout = timeout

        # create a buffer named frames and a queue for said buffer
        self.frames = deque(maxlen=self.bufsize)
        self.Q = None

        # create a video writer, writer thread, and bool for recording
        self.writer = None
        self.thread = None
        self.recording = False

    def update(self, frame):
        # add frame to frame buffer
        self.frames.appendleft(frame)

        # if we are recording then update the queue with the frame too
        if self.recording:
            self.Q.put(frame)

    def start(self, outputPath, fourcc, fps):
        self.recording = True

        # start the video writer and initialize the queue of frames that need to be written to file
        self.writer = cv2.VideoWriter(outputPath, fourcc, fps,
                                      (self.frames[0].shape[1], self.frames[0].shape[0]), True)
        self.Q = Queue()

        # add frames from dequeue to the queue
        for i in range(len(self.frames), 0, -1):
            self.Q.put(self.frames[i-1])

        # spawn a new thread to write frames to the video file
        self.thread = Thread(target=self.write, args=())
        self.thread.daemon = True
        self.thread.start()

    def write(self):
        while True:
            # if there is no recording going on exit the thread
            if not self.recording:
                return

            # check to see if there are entries in the queue
            if not self.Q.empty():
                # grab the next frame from the queue and write to video file
                frame = self.Q.get()
                self.writer.write(frame)

            else:
                time.sleep(self.timeout)

    def flush(self):
        # empty the queue by flushing all remaining frames to file
        while not self.Q.empty():
            frame = self.Q.get()
            self.writer.write(frame)

    def finish(self):
        # stop recording, join the thread, flush all remaining frames in the queue to file,
        # and release to writer pointer
        self.recording = False
        self.thread.join()
        self.flush()
        self.writer.release()
