#!/usr/bin/env python3

import cv2
import numpy as np
from clasificador import clasificar_oxido, segmentar_zona, pico_input
import serial
import time

def main():
    ########################################
    ### Conexión con la Pico ###
    ########################################
    # PUERTO REAL
    #SERIAL_PORT = '/dev/ttyACM0'
    # PUERTO SIMULADO
    # socat -d -d pty,raw,echo=0,link=/tmp/ttyPICO pty,raw,echo=0,link=/tmp/ttyPC
    # echo "1,123.32" > /tmp/ttyPICO

    SERIAL_PORT = "/tmp/ttyPC"
    BAUD_RATE = 115200
    try:
        # Intenta abrir el puerto serial
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Conectado al puerto: {SERIAL_PORT}")
        ser.flush() # Limpia cualquier dato pendiente
    except serial.SerialException as e:
        print(f"Error al abrir el puerto serial {SERIAL_PORT}: {e}")
        print("Asegúrate de que la Pico está conectada y el puerto es correcto.")
        exit()


    ########################################
    ### Conexión con la cámara ###
    ########################################
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise SystemExit("Cannot open camera")
    print("Cámara abierta correctamente.")
    # Hace una iteracion para crear las ventanas de visualización iniciales
    ret, frame = cap.read()
    cropped, drawn = segmentar_zona(frame, show_lines=True)
    oxido, binary_mask, orange_mask = clasificar_oxido(cropped)

    # Configuración de visualización
    window_viz = True

    # Bucle principal
    while True:
        try:
            # Lee la línea completa hasta que encuentra un '\n'
            if ser.in_waiting > 0:
                # Lee la línea y decodifica los bytes a string (quitando espacios y saltos de línea)
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    hall, posicion = pico_input(line)
                    print(f"--- MENSAJE RECIBIDO ---")
                    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Contenido: **{line}** -- Detección de hall: {hall}, Posición: {posicion}")
                    
                    if hall == 1:
                        ########################################
                        ### Procesamiento de la imagen ###
                        ########################################
                        ret, frame = cap.read()
                        if not ret:
                            break
                        # Se segmenta la imagen
                        cropped, drawn = segmentar_zona(frame, show_lines=True)
                        # Se clasifica la imagen
                        oxido, binary_mask, orange_mask = clasificar_oxido(cropped)
                        ########################################
                        ### Output de resultados ###
                        ########################################
                        if oxido:
                            tipo_falla = "O"
                            print(f"output2informe:O, {posicion:.2f}, path/to/image.jpg")
                            # TODO: Guardar imagen en path/to/image.jpg
                            # TODO: Escribir output en informe.txt
                        else:
                            tipo_falla = "N"
                            print("MAIN_LOOP: No se detecta falla")
                        
                    elif hall == -1:
                        print("Fin de carrera detectado. Saliendo del programa.")
                        break
        
        ########################################
        ### Manejo de excepciones ###
        ########################################
        # Si se desconecta el puerto
        except (serial.SerialException, OSError) as e:
            print(f"Error:{e} -- Se perdió la conexión serial. Reintentando...")
            time.sleep(5)
            try:
                ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                ser.flush()
                print("Reconexión exitosa.")
            except (serial.SerialException, OSError):
                pass # Continúa el bucle y sigue intentando

        # Si se cierra por teclado
        except KeyboardInterrupt:
            print("\nSaliendo del programa por KeyboardInterrupt...")
            break        

        ########################################
        ### Visualización en pantalla ###
        ########################################
        try:
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
                print("Saliendo del programa por tecla 'q'.")
                break

        except KeyboardInterrupt:
            print("\nSaliendo del programa por KeyboardInterrupt.")
            break  
        

    ########################################
    ### Limpieza final ###
    ########################################
    # Cierra OpenCV
    cap.release()
    cv2.destroyAllWindows()
    # Cierra el puerto al salir
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Puerto serial cerrado.")

if __name__ == "__main__":
    main()