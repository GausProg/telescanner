import cv2
import numpy as np

def detect_and_crop_paper(image_path):
    # Загрузка изображения
    img = cv2.imread(image_path)

    # Проверка, удалось ли загрузить изображение
    if img is None:
        print(f"Error: Unable to load the image at path: {image_path}")
        return

    # Преобразование изображения в оттенки серого
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Применение фильтра Гаусса для сглаживания изображения
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Применение адаптивного порогового преобразования
    _, threshold = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)

    # Поиск контуров
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Если обнаружены контуры
    if contours:
        # Нахождение контура с максимальной площадью (листа бумаги)
        max_contour = max(contours, key=cv2.contourArea)

        # Приближение контура до прямоугольника с более маленьким epsilon
        epsilon = 0.050 * cv2.arcLength(max_contour, True)
        approx = cv2.approxPolyDP(max_contour, epsilon, True)

        # Выделение листа бумаги на изображении
        cv2.drawContours(img, [approx], -1, (0, 255, 0), 2)

        # Вывод изображения с выделенным листом бумаги
        cv2.imshow("Detected Paper", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Выравнивание и обрезка листа бумаги
        rect = cv2.minAreaRect(approx)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # Выравнивание и обрезка
        width, height = int(rect[1][0]), int(rect[1][1])
        src_pts = box.astype("float32")
        dst_pts = np.array([[0, height - 1], [0, 0], [width - 1, 0], [width - 1, height - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(img, M, (width, height))

        # Вывод выровненного и обрезанного листа бумаги
        cv2.imshow("Warped Paper", warped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No contours found in the image.")

if __name__ == "__main__":
    image_path = "C:/Users/~~~/Desktop/2.jpg"
    detect_and_crop_paper(image_path)