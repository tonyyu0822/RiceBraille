# USAGE
# python scan.py --image images/page.jpg

# import the necessary packages
from dataclasses import dataclass
from typing import Any

from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_local
import ar_markers as ar
import cv2
import imutils
import numpy as np

import pyzbar.pyzbar as pyzbar


def transform_image(image, paper_dims=(825, 1100), output_image="scannedImage.jpg"):
    """
    :param image: image frame
    :param paper_dims: dimensions of paper (in pixels) to scale scanned image to
    :param output_image: name of file to write new image to
    :return: returns transformation matrix
    """
    # load the image and compute the ratio of the old height
    # to the new height, clone it, and resize it
    #ratio = image.shape[0] / 500.0
    orig = image.copy()
    #image = imutils.resize(image, height=500)

    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # show_image(gray)
    # TEST - maybe min value is too high? changed from 75 to 5
    edged = cv2.Canny(gray, 5, 200, True)
    # show_image(edged)

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour 
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    # # test code to loop over all contours
    # for c in cnts:
        # peri = cv2.arcLength(c, True)
        # approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # print("----------------------")
        # print(approx)
        # print("----------------------")

    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        print(approx)
        print(len(approx))

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx

            # to verify if we detected correct points
            colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 255), (100, 100, 100), (15, 205, 200)]
            for i in range(4):
                test = cv2.circle(image, (approx[i][0][0], approx[i][0][1]), radius=5, color=colors[i], thickness=-1)
            show_image(test)
            break
    
    # show the contour (outline) of the piece of paper
    print("STEP 2: Find contours of paper")
    # cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
    # image = cv2.resize(image, (1280,800))
    # cv2.imshow("Outline", image)
    # cv2.waitKey(0)
    #cv2.destroyAllWindows()

    # apply the four point transform to obtain a top-down
    # view of the original image
    M, warped, dims = four_point_transform(orig, screenCnt.reshape(4, 2))
    #find_markers(warped)
    # convert the warped image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    # warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    # T = threshold_local(warped, 11, offset=10, method="gaussian")
    # warped = (warped > T).astype("uint8") * 255

    # show the original and scanned images
    print("STEP 3: Apply perspective transform")

    # cv2.imwrite(output_image, cv2.resize(warped, paper_dims))
    # cv2.imshow("Scanned", cv2.resize(warped, paper_dims))
    # cv2.waitKey(0)

    print("Done transform initialization")

    return M, dims

def show_image(image):
    temp = cv2.resize(image, (1280, 800))
    cv2.imshow('test', temp)
    cv2.waitKey(0)

def transform_image_test(image):
    # uses harris corner detection instead of canny edge detection
    copy = image.copy()
    gray = cv2.cvtColor(copy, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gray = cv2.Canny(gray, 75, 200)
    show_image(gray)

    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)

    dst = cv2.dilate(dst, None)

    copy[dst>0.3 * dst.max()]=[0,0,255]

    test = cv2.resize(copy, (1280,800))
    cv2.imshow('dst', test)
    cv2.waitKey(0)


@dataclass(frozen=True)
class TransformMetadata:
    transformation_matrix: Any
    im_dims: (int, int)
    desired_dimensions: (int, int)


def transform_point(point: (int, int), transform_metadata: TransformMetadata):
    """
    :param point: point in original plane
    :param M: transformation matrix
    :return: prints point that point is transformed to in new plane
    """
    a = np.array([np.array([point], dtype='float32')])
    cur = cv2.perspectiveTransform(a, transform_metadata.transformation_matrix)
    x = cur.flatten()[0] * transform_metadata.desired_dimensions[0] / transform_metadata.im_dims[0]
    y = cur.flatten()[1] * transform_metadata.desired_dimensions[1] / transform_metadata.im_dims[1]
    return x, y

####### for debugging, remove later
def read_frame(cap, second):
    """
    Reads frame at given time stamp of video
    :param second: the time stamp of the video to read, in seconds
    :return: the frame at the input time stamp
    """
    # Read frame
    if second == 0:
        success, frame = cap.read()
    else:
        frame_count = int(second * cap.get(cv2.CAP_PROP_FPS))
        for i in range(frame_count):
            cap.grab()
        success, frame = cap.retrieve()

    # try:
        # frame = cv2.resize(frame, (1920, 1080))
    # except cv2.error as err:
        # print("Failed to read video")
        # raise err

    # self.vid_width = 1920
    # self.vid_height = 1080

    # quit if unable to read the video file
    if not success:
        print('Failed to read video')
        raise Exception("Failed to read video")

    return frame


def get_transform_video(video_path, desired_dimensions=(11.5625, 11.0)):
    cap = cv2.VideoCapture(video_path)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, video_length - 25)
    ret, frame = cap.read()
    
    m, im_dims = transform_image(frame)
    return TransformMetadata(m, im_dims, desired_dimensions)

if __name__ == '__main__':
    ############# FOR TESTING
    video_path = "./test_images/test_0.mp4"
    get_transform_video(video_path)
    for i in range(20, 70, 5):
        get_transform_video(video_path, i)

#transform_metadata = get_transform_video("test_images/test.mp4")
#print(transform_point((591, 263), transform_metadata))
# transform_point([0, 0], my_mat)


#get_transform_video("images/test_vid.mp4")
#cap = cv2.VideoCapture("images/angles.mp4")
#ret, frame = cap.read()
#cv2.imshow('first', frame)
#cv2.waitKey(0)
#print(cap.get(cv2.CAP_PROP_FPS))
#transform_point([0, 0], my_mat)
#test_angles("images/ar_dig.png", "images/angles.mp4")
