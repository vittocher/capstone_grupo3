#!/usr/bin/env python3
import cv2
import numpy as np
from pathlib import Path

def pico_input(line: str):
    """
    Recibe el input de la raspi pico.
    El input esperado es str(int, float)
    int es la deteccion (0 o 1 dependiendo del hall, -1 si se llega a fin de carrera)
    float es la posicion actual del robot
    Retorna (detection:int, position:float)
    """
    parts = line.split(',')
    detection = int(parts[0])
    position = float(parts[1])
    return detection, position

def clasificar_oxido(img:np.ndarray, hue_bound=[1,6], k_small:int=10, k_mid=40): #recibe una imagen en formato cv2
  # Paso 1
  # Convertir la imagen de BGR a HSV
  hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  # Separar los canales HSV
  hchannel, schannel, vchannel = cv2.split(hsv_img)

  # Paso 2
  # Definir los rangos de Hue para el color naranja (usando enteros directos)
  lower_orange_bound = hue_bound[0]
  upper_orange_bound = hue_bound[1]
  # Crear la máscara binaria para los tonos naranjas en el canal H1 (1 = naranjo, 0 = nada)
  orange_mask = cv2.inRange(hchannel, lower_orange_bound, upper_orange_bound)

  # Paso 3
  # Kernel pequeño para operaciones de cierre (dilatación y erosión)
  kernel_s = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_small, k_small))
  # Kernel mediano para operaciones de apertura (erosión y dilatación)
  kernel_m = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_mid, k_mid))
  # Aplicar operación de Cierre (Dilatación seguida de Erosión) con kernel_s
  closed_mask = cv2.dilate(orange_mask, kernel_s, iterations=1)
  closed_mask = cv2.erode(closed_mask, kernel_s, iterations=1)
  # Aplicar operación de Apertura (Erosión seguida de Dilatación) con kernel_m
  opened_mask = cv2.erode(closed_mask, kernel_m, iterations=1)
  opened_mask = cv2.dilate(opened_mask, kernel_m, iterations=1)

  # Paso 4
  # Contar el número de píxeles =! 0 en opened_mask
  count_nonzero_pixels = cv2.countNonZero(opened_mask)
  # Crear la variable booleana
  oxido_bool = count_nonzero_pixels > (k_mid/2)**2*3.15

  return oxido_bool, opened_mask, orange_mask

def segmentar_zona(img:np.ndarray, per:int=97, kernel_v_width:int=5, show_lines:bool=True) -> np.ndarray:
    """
    Retorna (cropped, out)
    - cropped: np.ndarray con el recorte entre las líneas
    - out: np.ndarray con la imagen original y líneas dibujadas, o None si show_lines=False
    """
    
    ## Paso 1 - Separar en HSV
    # Convertir la imagen de BGR a HSV
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Separar los canales HSV
    _, _, v1 = cv2.split(hsv_img)
    
    ## Paso 2 - Aplicar Sobel en x
    sobelx = cv2.Sobel(v1, cv2.CV_64F, 2, 0, ksize=13)
    sobelx = np.absolute(sobelx)
    sobelx_norm = cv2.normalize(sobelx, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    ## Paso 3 - Umbral por percentil
    p = np.percentile(sobelx_norm, per) # Obtiene el valor del percentil per de la imagen
    mask = (sobelx_norm > p).astype(np.uint8) # Filtra en base a ese valor
    
    
    ## Paso 4 - Perfil vertical
    mask2 = (mask > 0).astype(np.uint8)
    h, _ = mask2.shape[:2]
    # suma por columna (número de pixeles 1 en cada columna)
    col_sum = mask2.sum(axis=0).astype(np.float64)  # length = w
    # pad reflectivo de kernel_v_width//2 a ambos lados para conservar tamaño
    pad = kernel_v_width // 2
    col_sum_padded = np.pad(col_sum, pad_width=pad, mode='reflect')
    # convolución 1D con kernel de unos (suma de ventana de ancho kernel_v_width)
    kernel = np.ones(kernel_v_width, dtype=np.float64)
    conv = np.convolve(col_sum_padded, kernel, mode='valid')  # length = w
    # promedio normalizado por (h * kernel_v_width) -> proporción de píxeles '1' en cada ventana
    vertical_mean = conv / (h * float(kernel_v_width))

    
    ## Paso 5 - Selección de candidatos
    w = vertical_mean.shape[0]
    mid = w // 2
    left = vertical_mean[:mid]
    right = vertical_mean[mid:]
    if left.size:
        left_rel = int(np.argmax(left))
        left_idx = left_rel
    else:
        left_idx = 0
    if right.size:
        right_rel = int(np.argmax(right))
        right_idx = mid + right_rel
    else:
        right_idx = w - 1
    
    ## Paso 6 - Recorte
    cropped = img[:, left_idx:right_idx+1].copy()
    
    ## Paso 7 (opcional) - Retornar la imagen original con el borde dibujado
    if show_lines:
        out = img.copy()
        h, w = out.shape[:2]
        lx = int(np.clip(left_idx, 0, w-1))
        rx = int(np.clip(right_idx, 0, w-1))
        red_bgr = (0, 0, 255)  # OpenCV usa BGR
        cv2.line(out, (lx, 0), (lx, h-1), red_bgr, thickness=5)
        cv2.line(out, (rx, 0), (rx, h-1), red_bgr, thickness=5)
    else:
        out = None

    return cropped, out

if __name__ == "__main__":
    # Se testea con imágenes de prueba
    path0 = str(Path(__file__).parent) + "/"
    path1 = path0 + "B1.jpg"
    path2 = path0 + "B2.jpg"
    path3 = path0 + "B3.jpg"
    path4 = path0 + "B4.jpg"
    path5 = path0 + "B5.jpg"
    path6 = path0 + "B6.jpg"
    # Se cargan las imágenes
    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)
    img3 = cv2.imread(path3)
    img4 = cv2.imread(path4)
    img5 = cv2.imread(path5)
    img6 = cv2.imread(path6)
    img_array = [img1, img2, img3, img4, img5, img6]
    # Posiciones asociadas a las imágenes
    #pos_array = [10.002, 10.101, 10.433, 10.332, 9.999, 10.301]
    #paths = [path1, path2, path3, path4, path5, path6]
    
    # Se segmentan las imágenes
    cropped_array = []
    for imagen in img_array:
      cropped_array.append(segmentar_zona(imagen)[0])
    
 

    while True:
        try:
            # Se clasifican las imágenes e imprimen los resultados
            for crop in cropped_array:
                print("Imagen", clasificar_oxido(crop)[0])
        except KeyboardInterrupt:
            print("bye")
            break



