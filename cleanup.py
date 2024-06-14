import cv2 as cv
import numpy as np
import math

img = cv.imread("twolayer_sevenfold_weave_cp-1016x1024.jpg")
blur_size = 2

img = cv.GaussianBlur(img,(3,3),0)
blue_bits = cv.inRange(img, (100, 0, 0), (255, 100, 100))
red_bits = cv.inRange(img, (0, 0, 150), (100, 100, 255))
red_bits2 = cv.multiply(cv.bitwise_not(cv.multiply(cv.cvtColor(cv.absdiff(img, (0, 0, 255)), cv.COLOR_BGR2GRAY),
                               3)),8)
black_bits = cv.inRange(img, (0, 0, 0), (30, 30, 30))

cdst =  np.copy(img)

erosion_size=0
element = cv.getStructuringElement(2, (2 * erosion_size + 1, 2 * erosion_size + 1),
 (erosion_size, erosion_size))


cdstP2 = np.copy(img)

blue_lines = cv.HoughLinesP(cv.erode(blue_bits, element), 1, np.pi / 180, 5, None, 10, 8)
print(len(blue_lines))
for i in range(0, len(blue_lines)):
    l = blue_lines[i][0]
    cv.line(cdstP2, (l[0], l[1]), (l[2], l[3]), (0,255,0), 1, cv.LINE_AA)

cdstP = np.copy(img)

red_lines = cv.HoughLinesP(cv.dilate(red_bits2, element), 1, np.pi / 36, 10, None, 10, 5)
print(len(red_lines))
for i in range(0, len(red_lines)):
    l = red_lines[i][0]
    cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,255,0), 1, cv.LINE_AA)

#cv.imshow("Original", img)
cv.imshow("Red", red_bits)
cv.imshow("Red_ish", red_bits2)
#cv.imshow("Red lines", cdst)
cv.imshow("Red lines P", cdstP)
cv.imshow("Blue lines P", cdstP2)
#cv.imshow("Blue", blue_bits)
#cv.imshow("Black", black_bits)
k = cv.waitKey(0)

