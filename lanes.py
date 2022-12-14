import cv2
import numpy as np


def make_coordinates(image, line_parameters):
    # This function provides coordinates to the previously specified average slope and av. intercepts
    slope, intercept = line_parameters
    y1 = image.shape[0]
    y2 = int(y1*3/5)
    x1 = int((y1 - intercept)/slope)  #Since y = mx+b is our line equation
    x2 = int((y2 - intercept)/slope)
    return np.array([x1, y1, x2, y2]) #returning array or coordinates


def average_slope_intercept(image, lines):
    # This function calculates the average slopes of the left and right lines in
    # the lanes and uses the make_coordinates function to get the x,y coordinates
    # of the line in order to display the lines
    left_fit = []
    right_fit = []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)  # fits a polynomial of degree 1 to our x,y coordinates
        slope = parameters[0]
        intercept = parameters[1]
        if slope < 0:   # to determine if the line is on the right side or left side
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))
    left_fit_average = np.average(left_fit, axis = 0)    #averaging slopes on the left side of lane_image
    right_fit_average = np.average(right_fit, axis = 0)  #averaging slopes on the right side of lane_image
    left_line = make_coordinates(image, left_fit_average)
    right_line = make_coordinates(image, right_fit_average)
    return np.array([left_line, right_line])

def canny(image):
    # This function is used to convert our coulour image into a gradient image
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 50, 150)
    return canny

def display_lines(image, lines):
    # This function helps display lines on black image
    line_image = np.zeros_like(image)
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return line_image

def region_of_interest(image):
    height = image.shape[0]
    polygons = np.array([[(200, height), (1100, height), (550, 250)]])
    mask = np.zeros_like(image)          #black background

    cv2.fillPoly(mask, polygons, 255)
    # applying mask to our generated triangle (applying our desired image onto a black mask)

    masked_image = cv2.bitwise_and(image, mask)
    # to compute the bitwise & of both images takes the & function of each homologous
    # picture in both arrays, ultimately masking the canny image to only show
    # the region of interest traced by the polygon contour of the mask)

    return masked_image



#*******************************************************************************
# Code to detect lanes for a given whole video:
#*******************************************************************************

cap = cv2.VideoCapture("test2.mp4")
while (cap.isOpened()):
    _, frame = cap.read()
    canny_image = canny(frame)
    cropped_image = region_of_interest(canny_image)
    lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 100, np.array([]), minLineLength = 40, maxLineGap = 5)
     #  Note: The smaller the 2nd and 3rd arguents, the more precise the line detector will be and vice-versa.
     #  The 4th argument is the threshold, which signifies the minimum number of points
     #  that have to be alligned in a single straight line for it to be considered in the Hough mapping

    averaged_lines = average_slope_intercept(frame, lines)
    line_image = display_lines(frame, averaged_lines)
    combo_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    cv2.imshow('result', combo_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # to break out of the loop, press 'q'
        break
cap.release()
cv2.destroyAllWindows()
