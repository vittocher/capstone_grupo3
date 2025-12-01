#!/usr/bin/env python3

# Librerías para imágenes
import cv2
import numpy as np
from clasificador import clasificar_oxido, segmentar_zona, pico_input
# Librerías para comunicación serial
import serial
import time
# Librería para manejar paths de output
from pathlib import Path
# Librería para reiniciar el directorio de output
import shutil

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

    ########################################
    ### Parámetros inciales ###
    ########################################
    # Configuración de visualización
    window_viz = True
    # Crear/reset del directorio y del informe al inicio de la ejecución
    output_dir = Path(__file__).resolve().parent / "output_informe"
    # Si la carpeta ya existe, se elimina para reiniciar
    if output_dir.exists() and output_dir.is_dir():
        shutil.rmtree(output_dir)
    # Crear la carpeta de output
    output_dir.mkdir(parents=True, exist_ok=True)
    # Crear el archivo informe_raw.txt
    informe_path = output_dir / "informe_raw.txt"
    with open(informe_path, "w", encoding="utf-8") as f:
        f.write("tipo,posicion,path\n")

    ########################################
    ### Bucle principal ###
    ########################################
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
                            ### Guardar imagen en output_informe/filename.jpg
                            # Nombre del archivo - se usa timestamp para evitar sobreescrituras
                            timestamp = time.strftime('%Y%m%d_%H%M%S')
                            filename = f"{tipo_falla}_{posicion:.2f}_{timestamp}.jpg"
                            # Se guarda la imagen
                            save_path = output_dir / filename
                            ok = cv2.imwrite(str(save_path), frame)
                            if ok:
                                print(f"Imagen guardada en: {save_path}")
                                # Añadir línea al informe (append)
                                with open(informe_path, "a", encoding="utf-8") as finf:
                                    finf.write(f"{tipo_falla},{posicion:.2f},{str(save_path)}\n")
                                print(f"output2informe: O,{posicion:.2f},path/to/image.jpg")
                            else:
                                print("Error al guardar la imagen.")
                            
                        else:
                            tipo_falla = "N"
                            print("MAIN_LOOP: No se detecta falla")
                        
                    elif hall == -1:
                        ########################################
                        ### Fin de carrera ###
                        ########################################
                        tipo_falla = "E"
                        # Añadir línea al informe (append)
                        with open(informe_path, "a", encoding="utf-8") as finf:
                            finf.write(f"{tipo_falla},{posicion:.2f},N/A\n")
                        print(f"output2informe: F,{posicion:.2f},N/A")
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