import numpy as np
import cv2
import imutils

COLOR_RANGE: tuple[[int, int, int], [int, int, int]] = ((0, 125, 85), (53, 255, 255))
RADIUS_THRESHOLD: int = 10


def detect_ball(image: np.ndarray) -> np.ndarray:
    # print(image.shape)
    # grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(image, ksize=(5, 5), sigmaX=5, sigmaY=5, borderType=cv2.BORDER_DEFAULT)
    hsv_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)

    # create masked image
    # 1. remove all colors out of the target range
    masked_image = cv2.inRange(hsv_image, COLOR_RANGE[0], COLOR_RANGE[1])
    # 2. erosion (shrinks object -> remove small protuberances or noise from boundaries)
    masked_image = cv2.erode(masked_image, None, iterations=2)
    # 3. dilation (expands object -> fill small gaps or holes)
    masked_image = cv2.dilate(masked_image, None, iterations=2)

    # detect contours
    contours, hierarchy = cv2.findContours(masked_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # filter the contours to remove unnecessary ones
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    contours = imutils.grab_contours((contours, hierarchy))

    # check if any contours were detected
    if len(contours) > 0:
        # get the contours with the max area
        largest_area_contours = max(contours, key=cv2.contourArea)
        # fit a circle around the contours
        ((x, y), radius) = cv2.minEnclosingCircle(largest_area_contours)

        # extract the moments
        moments = cv2.moments(largest_area_contours)
        # get centroid from moments
        centroid = (int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"]))

        # check if the circle's radius is realistic
        if radius > RADIUS_THRESHOLD:
            # draw the circle
            cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            # draw the centroid
            cv2.circle(image, centroid, 5, (0, 0, 255), -1)

    return image
