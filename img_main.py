#!/usr/bin/env python3

import cv2
import numpy as np
from clasificador import clasificar_oxido, segmentar_zona

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
        # Se segmenta la imagen
        cropped, drawn = segmentar_zona(frame, show_lines=True)
        # Se clasifica la imagen
        oxido, binary_mask, orange_mask = clasificar_oxido(cropped)
        # Se crea la ventana de visualización
        cv2.putText(frame, f'Oxido: {oxido}', (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        combined = np.hstack((frame, cv2.cvtColor(orange_mask, cv2.COLOR_GRAY2BGR),cv2.cvtColor(binary_mask, cv2.COLOR_GRAY2BGR)))
        cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
        cv2.moveWindow('Output', 0, 0)
        cv2.resizeWindow('Output', 1600, 540)
        cv2.imshow('Output', combined)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()