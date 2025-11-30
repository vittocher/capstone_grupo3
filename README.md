Repositorio de procesamiento de imágenes del grupo 3 para el proyecto de CAPSTONE de Robótica de la PUC.
El proyecto desarrollado se ocupa de hacer una inspección visual de un cable de alta tensión, simulado en un tubo de PVC forrado con una textura apropiada. Esta inspección se hace con el objetivo explícito de detectar fallas de oxidación y fisuras. 
Los cuadernillos explican el funcionamiento del código de segmentación de zona de trabajo (separa el cable del fondo) y clasificación de imágenes para la detección de fallas de óxido. El algoritmo de clasificación para las fisuras se encuentra aparte del repositorio (por ahora).
Las imágenes se reciben a través de una cámara conectada por USB a una Raspberry Pi. Además, se reciben señales de un sensor Hall que detecta imanes, lo que indica cuándo se deben tomar imágenes para ser procesadas. Estas últimas señales son enviadas por una Raspberry Pi Pico, conectada por USB. 
El robot avanza autónomamente a través del cable, cosa de la que se encarga la Raspberry Pi Pico (razón por la cuál el código de tracción no se encuentra en este repositorio). El fin de carrera se lo informa la Raspberry Pi Pico a la Raspberry Pi 4, de la misma forma que comunica las señales del sensor Hall.
El output del código principal (img_main.py) es un informe .txt que reporta las fallas encontradas durante el recorrido. Al final de la carrera, se aplican un par de algoritmos sobre el informe.txt para que sea legible y coherente. 
Se usan las librerías OpenCV, Numpy y Matplotlib. Las dependencias no están configuradas correctamente en el repositorio (por falta de necesidad), por lo que se deben instalar a mano en caso de clonarlo. 
Si alguien que no sea del grupo 3 está viendo este repositorio, recomiendo ver los cuadernillos ipynb y no ver mucho los códigos de Python. Los primeros son mucho más didácticos que los últimos. 
Quedo atento cualquier cosa...
~ Vittorio Cherubini
