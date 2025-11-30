import serial
import time

# **GENERADO CON GEMINI**
# --- Configuración del Puerto Serial ---
# 1. Reemplaza '/dev/ttyACM0' con el puerto que identifiques en tu Pi 4
#    (Probablemente '/dev/ttyACM0' para la Pico)
# 2. Asegúrate de que el 'baudrate' (tasa de baudios) sea compatible. 
#    La Pico normalmente usa 115200 bps por defecto para su REPL/serial.
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
# --------------------------------------

try:
    # Intenta abrir el puerto serial
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Conectado al puerto: {SERIAL_PORT}")
    ser.flush() # Limpia cualquier dato pendiente
    
except serial.SerialException as e:
    print(f"Error al abrir el puerto serial {SERIAL_PORT}: {e}")
    print("Asegúrate de que la Pico está conectada y el puerto es correcto.")
    exit()

print("Esperando mensajes de la Raspberry Pi Pico...")

while True:
    try:
        # Lee la línea completa hasta que encuentra un '\n'
        if ser.in_waiting > 0:
            # Lee la línea y decodifica los bytes a string (quitando espacios y saltos de línea)
            line = ser.readline().decode('utf-8').strip()
            
            if line:
                print(f"--- MENSAJE RECIBIDO ---")
                print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Contenido: **{line}**")

                if line == "MAGNET_DETECTED":
                    # Aquí es donde puedes agregar la lógica que quieres ejecutar
                    print("¡ACCIÓN REQUERIDA! El imán fue detectado.")
                    # Ejemplo: Guardar en un log, activar un script, enviar una notificación.

    except serial.SerialException:
        print("Se perdió la conexión serial. Reintentando...")
        time.sleep(5)
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            ser.flush()
            print("Reconexión exitosa.")
        except serial.SerialException:
            pass # Continúa el bucle y sigue intentando
            
    except KeyboardInterrupt:
        print("\nSaliendo del programa.")
        break

    time.sleep(0.1) # Pequeña pausa para no saturar la CPU

# Cierra el puerto al salir
if 'ser' in locals() and ser.is_open:
    ser.close()
    print("Puerto serial cerrado.")