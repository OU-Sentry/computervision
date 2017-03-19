import imutils
import cv2


class MotionDetection:
    def __init__(self, accum_weight=0.5, delta_thresh=4, min_area=500):
        # larger the delta thresh, the less motion will be detected. Default 5
        self.isv2 = imutils.is_cv2()
        self.accum_weight = accum_weight
        self.delta_thresh = delta_thresh
        self.min_area = min_area

        # set the average image for motion detection aka reference frame
        self.average = None

    def update(self, image):
        # initialize the list of locations containing motion
        locations = []

        # if the average frame is None, initialize it
        if self.average is None:
            self.average = image.astype("float")
            return locations

        # calculate the weighted average between the current frame
        # and the previous frame, then compute the pixel-wise difference
        # between the current frame and the running average
        cv2.accumulateWeighted(image, self.average, self.accum_weight)
        frame_delta = cv2.absdiff(image, cv2.convertScaleAbs(self.average))

        # threshold the delta image and apply some dilations to help
        # fill in some holes
        thresh = cv2.threshold(frame_delta, self.delta_thresh,
                                255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        # find the contours in the threshold image
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if self.isv2 else contours[1]

        # loop through contours
        for c in contours:
            # add the contour to the locations list if
            # it exceeds the min area
            if cv2.contourArea(c) > self.min_area:
                locations.append(c)

        # return the set of locations
        return locations
