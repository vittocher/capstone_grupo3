import cv2
import numpy as np
from clasificador import clasificar_oxido

def main():
    cap = cv2.VideoCapture(0)  # or VideoCapture('/dev/video0', cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise SystemExit("Cannot open camera")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # frame is BGR — ready for clasificar_oxido
        oxido = clasificar_oxido(frame)
        cv2.putText(frame, f'Oxido: {oxido}', (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()