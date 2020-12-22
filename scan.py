# USAGE
# python scan.py --image images/page.jpg

# import the necessary packages
from dataclasses import dataclass
from typing import Any

from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_local
import cv2
import imutils
import numpy as np

screenCnt = []

def click(event, x, y, flag, image):
    global screenCnt
    if event == cv2.EVENT_LBUTTONDOWN:
        coords = [[x, y]]
        screenCnt.append(coords)

# NOTE: no idea what paper_dims is for
def transform_image(image, paper_dims=(825, 1100), output_image="scannedImage.jpg", black_background=True, automatic=True):
    """
    :param image: image frame
    :param paper_dims: dimensions of paper (in pixels) to scale scanned image to
    :param output_image: name of file to write new image to
    :param black_background: if True, will perform page calibration by casting background to black 
    :param automatic: if True, will perform page calibration automatically
    :return: returns transformation matrix
    """
    global screenCnt

    # preserve original image
    orig = image.copy()
    
    if automatic:
        # page calibration filtering method depends on if background needs to be cast to black
        if black_background:
            # mask everything from neon green to black: helps distinguish page from background
            # first, turn page to black and background to white
            lower = np.array([30, 50, 50])
            upper = np.array([50, 255, 255])
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            # then, flip color so background is black and page is white
            mask[mask > 0] = 1
            new_mask = np.subtract(np.ones(np.shape(mask)), mask)
            new_mask = new_mask.astype('uint8')
            image = cv2.bitwise_and(image, image, mask=new_mask)

            # convert the image to grayscale, blur it, and find edges in image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 75, 200)

        # otherwise, use double-blur method (when this method works, it seems to tags corners more accurately, but doesn't always work)
        else:
            # convert the image to grayscale, blur it, and find edges
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # double blur ensures that braille dots are not picked up by canny filter
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            blurred = cv2.GaussianBlur(blurred, (5, 5), 0)
            edged = cv2.Canny(blurred, 5, 200, True)

        # find the contours in the edged image, keeping only the largest ones, and initialize the screen contour 
        cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

        # loop over the contours
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            print(approx)
            print(len(approx))

            # if our approximated contour has four points, then we can assume that we have found our screen
            if len(approx) == 4:
                screenCnt = approx

                # to verify if we detected correct points
                red = (0, 0, 255)
                # colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 255), (255, 255, 255), (255, 255, 255)]
                for i in range(4):
                    with_corners = cv2.circle(orig, (approx[i][0][0], approx[i][0][1]), radius=5, color=red, thickness=-1)
                show_image(with_corners)
                break
    else:
        cv2.setMouseCallback('CapturedImage', click, image)
        while(len(screenCnt) < 4):
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                print('Image cropped at coordinates: {}'.format(screenCnt))
                cv2.destroyAllWindows()
                break
        screenCnt = np.asarray(screenCnt)
    
    # check if we successfully found our screen
    if screenCnt == []:
        return None, None

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
    show_image(warped)
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
    """
    Displays image using cv2, but rescaled to fit on standard screen
    
    :param image: image to be displayed
    """
    resized = cv2.resize(image, (1280, 800))
    cv2.imshow('Image', resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


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


def get_transform_video(video_path, desired_dimensions=(11.5, 11.0), black_background=True):
    cap = cv2.VideoCapture(video_path)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    m = None
    for i in range(75, 25, -5):
        cap.set(cv2.CAP_PROP_POS_FRAMES, video_length - i)
        ret, frame = cap.read()
        transform_image(frame, automatic=False)
        m, im_dims = transform_image(frame, black_background=black_background)
        if m is not None:
            break

    # if m is still None after this, then default to automatic
    if m is None:
        m, im_dims = transform_image(video_path, automatic=False)

    return TransformMetadata(m, im_dims, desired_dimensions)

if __name__ == '__main__':
    video_path = "./test_images/test_0.mp4"
    get_transform_video(video_path)

#transform_metadata = get_transform_video("test_images/test.mp4")
#print(transform_point((591, 263), transform_metadata))
# transform_point([0, 0], my_mat)