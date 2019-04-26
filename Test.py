import cv2
import numpy as np
import sys

hue=0.000
ammountOfBilirubin=0.000

def printValue(event,x,y,flags,param):   
    
    print img[y,x],hsv[y,x]

img=cv2.imread('X.jpg')
cv2.namedWindow("image")
cv2.imshow("image",img)
img1=img.copy()
img2=img.copy()

img1 = cv2.medianBlur(img1,5)
##print img.shape
img[img1[:,:,1] <= 160]= 0
img[img1[:,:,2] <= 190]= 0
hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
lower_value = np.array([20,10,180])
upper_value = np.array([100,200,240])
mask = cv2.inRange(hsv, lower_value, upper_value)
res = cv2.bitwise_and(img,img, mask= mask)
u= hsv[res[:,:,0] >0 ]
c=img2[res[:,:,0] >0 ]
average_color = np.average(u, axis=0)
average_colorc = np.average(c, axis=0)
[H, S, V] = average_color
[R, G, B] = average_colorC
print average_color
print average_colorc
print R
print H
print S
cv2.setMouseCallback("image",printValue)

while(1):
    
    cv2.imshow("image",res)
    if cv2.waitKey(20) & 0xFF == 27:
        break
cv2.destroyAllWindows()
