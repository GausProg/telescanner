import cv2
import numpy as np
import base64
from io import BytesIO

def detect_and_crop_paper(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print(f"Error: Unable to load the image at path: {image_path}")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, threshold = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        epsilon = 0.050 * cv2.arcLength(max_contour, True)
        approx = cv2.approxPolyDP(max_contour, epsilon, True)

        rect = cv2.minAreaRect(approx)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        width, height = int(rect[1][0]), int(rect[1][1])
        src_pts = box.astype("float32")
        dst_pts = np.array([[0, height - 1], [0, 0], [width - 1, 0], [width - 1, height - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(img, M, (width, height))

        _, img_encoded = cv2.imencode(".jpg", warped)
        img_bytes = img_encoded.tobytes()

        return img_bytes
    else:
        print("No contours found in the image.")
        return None

def imagination(image_path):
    #image_path = "test2.jpg"
    result_image_bytes = detect_and_crop_paper(image_path)

    if result_image_bytes is not None:
        with open("output_image.jpg", "wb") as f:
            f.write(result_image_bytes)
    return "output_image.jpg"