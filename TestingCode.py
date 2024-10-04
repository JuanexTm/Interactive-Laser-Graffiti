import cv2
import numpy as np
import pygame
import time

# Inicialización de la cámara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()


grafiti = None
ultimo_punto = None
laser_activo = False
colorElegido = False
colorLaser = 0,0,0
hayPintura = True

# Inicialización de botones de color y posiciones
colores_botones = [
    ((255, 0, 0), 'Azul'), ((0, 0, 255), 'Rojo'),
    ((255, 90, 160), 'Lila'), ((0, 255, 255), 'Amarillo'),
    ((0, 255, 0), 'Verde'), ((255, 0, 255), 'Rosa'),
    ((255, 255, 255), 'Blanco')
]

botones = []
altura_botones = cap.get(4) - 50  # Altura de los botones
radio_boton = 30  # Radio de los botones
ancho_frame = int(cap.get(3))

for i, (color, nombreColor) in enumerate(colores_botones):
    x_pos = ancho_frame * (i + 1) // 8
    botones.append((color, (x_pos, int(altura_botones)), nombreColor))

btn_Reset = (ancho_frame - 60, int(cap.get(4) // 8))
btn_Borrar = (ancho_frame - 60, int(cap.get(4) * 2 // 8))


# Parámetros del slider
slider_min = 10  # Tamaño mínimo del trazo
slider_max = 51  # Tamaño máximo del trazo
slider_width = 20  # Ancho del slider
slider_height = cap.get(4) * 0.8  # Altura del área del slider (80% de la altura de la pantalla)
center_y = int(cap.get(4) // 2)  # Centrar en el eje Y de la pantalla
slider_x = 25  # Posición en X del slider
slider_pos = center_y  # Posición inicial del control del slider
tamaño_trazo = 20  # Tamaño inicial del trazo


# Función para calcular la distancia euclidiana entre dos puntos
def distancia(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

pygame.mixer.init()
# pygame.mixer.music.load('spray.mp3')

spraySfx = pygame.mixer.Sound("spray.mp3")

# Parámetros del temporizador
tiempo_total = 10  # 90 segundos
tiempo_restante = tiempo_total
start_time = None  # Momento en que se empieza a pintar
tiempo_terminado = None

# Parámetros de la barra de pintura
barra_ancho_total = cap.get(3) - 100  # Ancho total de la barra
barra_alto = 20  # Alto de la barra
barra_x = 50  # Posición X de la barra
barra_y = int(cap.get(4) - 10)  # Posición Y de la barra, debajo de los botones

# ============================================= Temporizador y barra =====================================================
def dibujar_barra_pintura(frame, tiempo_restante):
    # Calculamos el ancho proporcional de la barra basado en el tiempo restante
    ancho_barra = int((tiempo_restante / tiempo_total) * barra_ancho_total)
    
    # Asegurarnos de que las coordenadas sean enteros
    cv2.rectangle(frame, (int(barra_x), int(barra_y)), (int(barra_x + barra_ancho_total), int(barra_y + barra_alto)), (255, 255, 255), 2)
    
    # Dibujar la barra que representa la pintura restante
    if ancho_barra > 0:
        cv2.rectangle(frame, (int(barra_x), int(barra_y)), (int(barra_x + ancho_barra), int(barra_y + barra_alto)), (0, 255, 0), -1)


# ============================================= Actualización del tiempo =================================================
def actualizar_tiempo():
    global start_time, tiempo_restante
    if laser_activo and colorElegido is True and colorLaser is not (0,0,0):
        if start_time is None:
            # Si empezamos a pintar, registramos el tiempo de inicio
            start_time = time.time()
        else:
            # Calculamos cuánto tiempo ha pasado desde que se empezó a pintar
            tiempo_pasado = time.time() - start_time
            start_time = time.time()  # Actualizamos el tiempo de inicio para la siguiente vez
            tiempo_restante -= tiempo_pasado  # Reducimos el tiempo restante
            tiempo_restante = max(tiempo_restante, 0)  # No dejamos que el tiempo sea negativo


    else:
        # Si no estamos pintando, pausamos el temporizador
        start_time = None

while True:
    # Capturar cada frame
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer el frame de la cámara.")
        break
    
    # Inicializar la imagen de grafiti con el mismo tamaño que el frame
    if grafiti is None:
        grafiti = np.zeros_like(frame)

    # Convertir la imagen de BGR a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Definir el rango de color rojo en HSV
    lower_red = np.array([0, 0, 255])
    upper_red = np.array([255, 255, 255])

    # Crear la máscara para el rango de color rojo
    mask = cv2.inRange(hsv, lower_red, upper_red)

    # Encontrar el punto máximo en la máscara
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)

    # Dibujar un círculo en la posición detectada
    cv2.circle(frame, maxLoc, 20, (0, 0, 255), 2, cv2.LINE_AA)

    # Determinar si el láser está activo basado en el valor máximo
    # Puedes ajustar el umbral según tus necesidades
    umbral_valor_max = 250  # Valor máximo de V en HSV para considerar el láser activo
    if maxVal > umbral_valor_max:
        punto_actual = maxLoc
        if laser_activo and ultimo_punto is not None and colorElegido and hayPintura:
            # Dibujar una línea en la imagen de grafiti
            cv2.line(grafiti, ultimo_punto, punto_actual, (colorLaser), tamaño_trazo)  # Rojo en BGR
        # Actualizar el último punto y marcar el láser como activo
        ultimo_punto = punto_actual
        laser_activo = True

        # pygame.mixer.music.play(loops=-1)
        if colorLaser == (0,0,0):
            spraySfx.stop()
        else:
            spraySfx.play(loops=-1)

    else:
        # Si el láser no está detectado, resetear el estado
        laser_activo = False
        ultimo_punto = None

        #pygame.mixer.music.stop()
        spraySfx.stop()


    # Actualizar el tiempo si el láser está pintando
    actualizar_tiempo()

    # Dibujar la barra de pintura
    dibujar_barra_pintura(frame, tiempo_restante)

    if tiempo_restante == 0:
        hayPintura = False
        spraySfx.stop()
        tiempo_terminado = True
        
        


# ============================================ Botones ===================================================

    for color, (x, y), nombreColor in botones:
        cv2.circle(frame, (x, y), radio_boton, color, -1)
        if distancia(maxLoc, (x, y)) < radio_boton:
            colorElegido = True
            print(f"Color {nombreColor} activado")
            colorLaser = color

    # Botón de reset
    cv2.circle(frame, btn_Reset, radio_boton, (0, 0, 0), -1)
    if distancia(maxLoc, btn_Reset) < radio_boton:
        print("Canvas borrado")
        colorElegido = False
        grafiti = np.zeros_like(frame)
        # colorLaser = (0, 0, 0)
        laser_activo = False

    # Botón de borrar
    cv2.circle(frame, btn_Borrar, radio_boton, (255, 255, 255), -1)
    if distancia(maxLoc, btn_Borrar) < radio_boton:
        colorElegido = True
        print("Borrador activado")
        colorLaser = (0, 0, 0)


    # ============================================= Slider =====================================================

    # Dibujar el área del slider centrada en el eje Y
    top_y = int(center_y - slider_height / 2)
    bottom_y = int(center_y + slider_height / 2)
    cv2.rectangle(frame, (slider_x, top_y), (slider_x + slider_width, bottom_y), (100, 100, 100), -1)

    # Dibujar el control del slider
    cv2.rectangle(frame, (slider_x, slider_pos - 10), (slider_x + slider_width, slider_pos + 10), (255, 255, 255), -1)

    # Comprobar si el láser está dentro del área del slider
    if slider_x < maxLoc[0] < slider_x + slider_width and top_y < maxLoc[1] < bottom_y:
        slider_pos = maxLoc[1]
        tamaño_trazo = int(np.interp(slider_pos, [top_y, bottom_y], [slider_max, slider_min]))

    # Mostrar el tamaño del trazo
    cv2.putText(frame, f'{tamaño_trazo}', (slider_x + 40, top_y - 10), cv2.FONT_ITALIC, 1, (255, 255, 255), 2)

    # ==================================================================================================


    # Combinar la imagen de grafiti con el frame original
    combined = cv2.addWeighted(frame, 0.7, grafiti, 0.3, 0)

    # Mostrar el frame combinado
    cv2.imshow('Track Laser', combined)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
