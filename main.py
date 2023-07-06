import cv2

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Image', frame)
        cv2.waitKey(0)
    cap.release()
    cv2.destroyAllWindows()
