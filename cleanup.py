import cv2 as cv
import numpy as np
import math

img = cv.imread("twolayer_sevenfold_weave_cp-1016x1024.jpg")

blue, green, red = cv.split(img)
not_blue, not_green, not_red= cv.split(cv.bitwise_not(img))

def channel_filter(channels: list, shift=25, mul=1.2):
    current = channels[0]
    for next_channel in channels[1:]:
        current = cv.multiply(current, next_channel, scale=1/255)
    return cv.multiply(cv.subtract(current, shift), mul)

red_only = channel_filter([red, not_blue, not_green])
blue_only = channel_filter([blue, not_red, not_green])
black_only = channel_filter([not_red, not_blue, not_green], 130, 2)


lines = cv.createLineSegmentDetector(cv.LSD_REFINE_ADV)
red_lines, widths, somethings, blah = lines.detect(red_only)
blue_lines, widths, somethings, blah = lines.detect(blue_only)
black_lines, widths, somethings, blah = lines.detect(black_only)

simplified_lines = []

def print_lines_on(target, lines):
    result = np.copy(target)
    for i in range(0, len(lines)):
        #if widths[i] > 2:
        l = lines[i][0]
        cv.line(
            result,
            (int(l[0]), int(l[1])),
            (int(l[2]), int(l[3])),
            (0, 255, 0),
            1,
            cv.LINE_AA,
        )
        cv.circle(result, (int(l[0]), int(l[1])), 5, (0, 0, 255), 1, cv.LINE_AA)
        cv.circle(result, (int(l[2]), int(l[3])), 5, (0, 0, 255), 1, cv.LINE_AA)
    return result



# cv.imshow("Original", img)
cv.imshow("Red Bits", red_only)
cv.imshow("Blue Bits", blue_only)
cv.imshow("Black Bits", black_only)
cv.imshow("Red Lines", print_lines_on(img, red_lines))
cv.imshow("Blue Lines", print_lines_on(img, blue_lines))
cv.imshow("Black Lines", print_lines_on(img, black_lines))
# cv.imshow("Blue", blue_bits)
# cv.imshow("Black", black_bits)
k = cv.waitKey(0)
