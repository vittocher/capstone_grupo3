import cv2
import numpy as np

def clasificar_oxido(img:np.ndarray): #recibe una imagen en formato cv2
  # Paso 1
  # Convertir la imagen de BGR a HSV
  hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  # Separar los canales HSV
  hchannel, schannel, vchannel = cv2.split(hsv_img)

  # Paso 2
  # Definir los rangos de Hue para el color naranja (usando enteros directos)
  lower_orange_bound = 1
  upper_orange_bound = 6
  # Crear la máscara binaria para los tonos naranjas en el canal H1 (1 = naranjo, 0 = nada)
  orange_mask = cv2.inRange(hchannel, lower_orange_bound, upper_orange_bound)

  # Paso 3
  # Kernel pequeño (5x5) para operaciones de cierre (dilatación y erosión)
  kernel_s = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
  # Kernel mediano (10x10) para operaciones de apertura (erosión y dilatación)
  kernel_m = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30, 30))
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
  oxido_bool = count_nonzero_pixels > 35

  return oxido_bool, opened_mask, orange_mask


if __name__ == "__main__":
    # Se testea con imágenes de prueba
    path1 = "/home/grupo3/grupo3_ws/B1.jpg"
    path2 = "/home/grupo3/grupo3_ws/B2.jpg"
    path3 = "/home/grupo3/grupo3_ws/B3.jpg"
    path4 = "/home/grupo3/grupo3_ws/B4.jpg"
    path5 = "/home/grupo3/grupo3_ws/B5.jpg"
    path6 = "/home/grupo3/grupo3_ws/B6.jpg"
    # Se cargan las imágenes
    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)
    img3 = cv2.imread(path3)
    img4 = cv2.imread(path4)
    img5 = cv2.imread(path5)
    img6 = cv2.imread(path6)
    img_array = [img1, img2, img3, img4, img5, img6]
    # Posiciones asociadas a las imágenes
    pos_array = [10.002, 10.101, 10.433, 10.332, 9.999, 10.301]
    paths = [path1, path2, path3, path4, path5, path6]
    # Se clasifican las imágenes e imprimen los resultados
    for imagen in img_array:
        print("Imagen", clasificar_oxido(imagen)[0])

