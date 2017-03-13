from threading import Thread
import cv2


class WebCamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # variable to keep track of thread status
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # updating the thread until stopped
        while True:
            # if our thread var indicator is set stop
            if self.stopped:
                return

            # otherwise grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the most recently read frame
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
