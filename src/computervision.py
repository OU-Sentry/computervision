from eventrecording import EventDetection
from imagestitching import Stitcher
from motiondetection import MotionDetection
from videostream import WebCamVideoStream
from videoupload import Upload
import argparse
import datetime
import numpy as np
import time
import imutils
import cv2

arg = argparse.ArgumentParser()
arg.add_argument("-o", "--output", default="/pi/videos/", help="path to output video file")
arg.add_argument("-f", "--fps", type=int, default=15,
                 help="FPS of output video")
arg.add_argument("-b", "--buffer-size", type=int, default=60,
                 help="buffer size of video clip writer")
arg.add_argument("-c", "--codec", type=str, default="MJPG",
                 help="codec of output file")
args = vars(arg.parse_args())

# captures on camera zero what ever that may be
# camera one must be on the right and camera two must be on the left
# for image stitching to work!
print("[INFO] warming up the camera...")
camera1 = WebCamVideoStream(src=1).start()
camera2 = WebCamVideoStream(src=0).start()
time.sleep(1.00)
print("[INFO] Cameras active")

# initialize file monitoring for video files
upload = Upload(args["output"])

# initialize image stitcher
stitcher = Stitcher()
# initialize motion detection from the camera input/inputs
motion = MotionDetection()

# initialize event detection writer
eventdetection = EventDetection(bufsize=args["buffer_size"])

# set number of frames where no even has occurred to zero
consecframes = 0

# set counter for total number of frames
totalframes = 0

# use try/finally to make sure calls to stop threads are executed
try:
    # start upload thread
    upload.start()
    # loop over feed from the camera or the video file
    while True:
        # initialize a list of frames that have been processed
        frames = []

        # text to be displayed on window of video
        text = "Not Detected"

        updateconsecframes = True

        camera1stream = camera1.read()
        camera2stream = camera2.read()

        camera1stream = imutils.resize(camera1stream, width=600)
        camera2stream = imutils.resize(camera2stream, width=600)

        # left camera (camera2) must be input first, right
        # camera second (camera1)
        result = stitcher.stitch([camera2stream, camera1stream])

        if result is None:
            print("[INFO] homography could not be computed... ")
            break

        # convert the frame to grayscale and blur it slightly
        # update the motion detector as well
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        locs = motion.update(gray)

        # allow motion detection to accumulate set of frames for better avg
        if totalframes < 32:
            frames.append(result)
            totalframes += 1
            continue

        # check to see if motion was detected
        if len(locs) > 0:
            # initialize the min and max X,Y coordinates respectively
            (minX, minY) = (np.inf, np.inf)
            (maxX, maxY) = (-np.inf, -np.inf)

            # loop over the locations of motion and accumulate the
            # min and max locations of the bounding boxes
            for l in locs:
                (x, y, w, h) = cv2.boundingRect(l)
                (minX, maxX) = (min(minX, x), max(maxX, x + w))
                (minY, maxY) = (min(minY, y), max(maxY, y + h))

            # draw the bounding box on the frame
            cv2.rectangle(result, (minX, minY), (maxX, maxY),
                          (0, 0, 255), 3)

            text = "Detected"
            consecframes = 0
            updateconsecframes = False

            # if we are not yet saving frames to a file, start now
            if not eventdetection.recording:
                timestamp = datetime.datetime.now()
                p = "{}/{}.avi".format(args["output"],
                                       timestamp.strftime("%Y%m%d-%H%M%S"))
                eventdetection.start(p, cv2.VideoWriter_fourcc(*args["codec"]),
                                     args["fps"])

        # update the frames list
        frames.append(result)

        # if no event occured
        if updateconsecframes:
            consecframes += 1

        # update the key frame clip buffer
        eventdetection.update(result)

        # if we are recording and no motion has taken place within the buffer size
        if eventdetection.recording and consecframes == args["buffer_size"]:
            eventdetection.finish()

        totalframes += 1
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

        cv2.putText(result, timestamp, (10, result.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # show the output of the images
        # cv2.imshow("result", result)
        # v2.imshow("left", camera2stream)
        # v2.imshow("right", camera1stream)

finally:
    # clean up camera connections
    print("[INFO] shutting down cameras...")
    cv2.destroyAllWindows()
    camera1.stop()
    camera2.stop()
    upload.stop()
