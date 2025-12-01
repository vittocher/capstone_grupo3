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

    # Configuración de visualización
    window_viz = True

    # Bucle principal
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ########################################
        ### Procesamiento de la imagen ###
        ########################################
        # Se segmenta la imagen
        cropped, drawn = segmentar_zona(frame, show_lines=True)
        # Se clasifica la imagen
        oxido, binary_mask, orange_mask = clasificar_oxido(cropped)

        ########################################
        ### Resultados en consola ###
        ########################################
        if oxido:
            tipo_falla = "O"
            #print("Oxido detectado")
        else:
            tipo_falla = "N"
            #print("MAIN_LOOP: No se detecta falla")
        

        ########################################
        ### Visualización en pantalla ###
        ########################################
        if window_viz:
            # Se escribe el resultado sobre frame
            cv2.putText(frame, f'Oxido: {oxido}', (10,60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0,255,0), 4)
            # Definir tamaño común para todas las imágenes
            size = (320, 240)
            frame_r = cv2.resize(frame, size)
            orange_mask_r = cv2.resize(orange_mask, size)
            binary_mask_r = cv2.resize(binary_mask, size)
            cropped_r = cv2.resize(cropped, size)
            drawn_r = cv2.resize(drawn, size)
            # Primera fila: frame, drawn, cropped
            row1 = np.hstack((frame_r, drawn_r,  cropped_r))
            # Segunda fila: orange_mask, binary_mask (repetir uno para alinear 3 columnas)
            row2 = np.hstack((cv2.cvtColor(orange_mask_r, cv2.COLOR_GRAY2BGR), cv2.cvtColor(binary_mask_r, cv2.COLOR_GRAY2BGR), np.zeros_like(frame_r)))
            # Combinar filas
            combined = np.vstack((row1, row2))
            cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
            cv2.moveWindow('Output', 0, 0)
            cv2.resizeWindow('Output', 960, 480)
            cv2.imshow('Output', combined)
        
        ########################################
        ### Salida del bucle ###
        ########################################
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()