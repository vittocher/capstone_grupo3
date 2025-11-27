import cv2
import numpy as np
from clasificador import clasificar_oxido

def main():
    # Abrir la cámara
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise SystemExit("Cannot open camera")

    # Bucle principal
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Se clasifica la imagen
        oxido, binary_mask = clasificar_oxido(frame)
        cv2.putText(frame, f'Oxido: {oxido}', (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow('Camera', frame)
        cv2.imshow('Binary Mask', binary_mask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()