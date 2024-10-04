import cv2
import numpy as np
import pygame


# Inicialización de la cámara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()


grafiti = None
ultimo_punto = None
laser_activo = False
colorLaser = 0,0,0


# Función para calcular la distancia euclidiana entre dos puntos
def distancia(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

pygame.mixer.init()
# pygame.mixer.music.load('spray.mp3')

spraySfx = pygame.mixer.Sound("spray.mp3")

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
        if laser_activo and ultimo_punto is not None:
            # Dibujar una línea en la imagen de grafiti
            cv2.line(grafiti, ultimo_punto, punto_actual, (colorLaser), 20)  # Rojo en BGR
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


    

# ============================================ Botones ===================================================

# Color Azul
    btn_Azul_x = frame.shape[1] // 8
    btn_Azul_y = frame.shape[0] - 50
    radio_boton = 30  # Radio del botón circular

    # Dibujar el botón en el frame
    cv2.circle(frame, (btn_Azul_x, btn_Azul_y), radio_boton, (255, 0, 0), -1)

    if distancia(maxLoc, (btn_Azul_x, btn_Azul_y)) < radio_boton:
        print("Color Azul activado")
        colorLaser = 255, 0, 0

# Color Rojo
    btn_Rojo_x = frame.shape[1] * 2 // 8
    btn_Rojo_y = frame.shape[0] - 50
    radio_boton = 30  # Radio del botón circular

    # Dibujar el botón en el frame
    cv2.circle(frame, (btn_Rojo_x, btn_Rojo_y), radio_boton, (0, 0, 255), -1)

    if distancia(maxLoc, (btn_Rojo_x, btn_Rojo_y)) < radio_boton:
        print("Color Rojo activado")
        colorLaser = 0, 0, 255

# Color Lila
    btn_Lila_x = frame.shape[1] * 3 // 8
    btn_Lila_y = frame.shape[0] - 50
    radio_boton = 30  # Radio del botón circular

    # Dibujar el botón en el frame
    cv2.circle(frame, (btn_Lila_x, btn_Lila_y), radio_boton, (255, 90, 160), -1)

    if distancia(maxLoc, (btn_Lila_x, btn_Lila_y)) < radio_boton:
        print("Color Lila activado")
        colorLaser = 255, 90, 160

# Color Amarillo
    btn_Amarillo_x = frame.shape[1] * 4 // 8
    btn_Amarillo_y = frame.shape[0] - 50
    radio_boton = 30  # Radio del botón circular

    # Dibujar el botón en el frame
    cv2.circle(frame, (btn_Amarillo_x, btn_Amarillo_y), radio_boton, (0, 255, 255), -1)

    if distancia(maxLoc, (btn_Amarillo_x, btn_Amarillo_y)) < radio_boton:
        print("Color Amarillo activado")
        colorLaser = 0, 255, 255

# Color Verde
    btn_Verde_x = frame.shape[1] * 5 // 8
    btn_Verde_y = frame.shape[0] - 50
    radio_boton = 30  # Radio del botón circular

    # Dibujar el botón en el frame
    cv2.circle(frame, (btn_Verde_x, btn_Verde_y), radio_boton, (0, 255, 0), -1)

    if distancia(maxLoc, (btn_Verde_x, btn_Verde_y)) < radio_boton:
        print("Color Verde activado")
        colorLaser = 0, 255, 0

# Color Rosa
    btn_Rosa_x = frame.shape[1] * 6 // 8
    btn_Rosa_y = frame.shape[0] - 50
    radio_boton = 30  # Radio del botón circular

    # Dibujar el botón en el frame
    cv2.circle(frame, (btn_Rosa_x, btn_Rosa_y), radio_boton, (255, 0, 255), -1)

    if distancia(maxLoc, (btn_Rosa_x, btn_Rosa_y)) < radio_boton:
        print("Color Rosa activado")
        colorLaser = 255, 0, 255

# Color Blanco
    btn_Blanco_x = frame.shape[1] * 7 // 8
    btn_Blanco_y = frame.shape[0] - 50
    radio_boton = 30  # Radio del botón circular

    # Dibujar el botón en el frame
    cv2.circle(frame, (btn_Blanco_x, btn_Blanco_y), radio_boton, (255, 255, 255), -1)

    if distancia(maxLoc, (btn_Blanco_x, btn_Blanco_y)) < radio_boton:
        print("Color Blanco activado")
        colorLaser = 255, 255, 255

# Reset
    btn_Reset_x = frame.shape[1] - 50
    btn_Reset_y = frame.shape[0] // 8
    radio_boton = 30  # Radio del botón circular

    # Dibujar el botón en el frame
    cv2.circle(frame, (btn_Reset_x, btn_Reset_y), radio_boton, (0, 0, 0), -1)

    if distancia(maxLoc, (btn_Reset_x, btn_Reset_y)) < radio_boton:
        print("Canvas borrado")
        grafiti = np.zeros_like(frame)
        colorLaser = 0, 0, 0

# Borrador (Color Negro)
    btn_Negro_x = frame.shape[1] - 50
    btn_Negro_y = frame.shape[0] * 2 // 8
    radio_boton = 30  # Radio del botón circular

    # Dibujar el botón en el frame
    cv2.circle(frame, (btn_Negro_x, btn_Negro_y), radio_boton, (255, 255, 255), -1)

    if distancia(maxLoc, (btn_Negro_x, btn_Negro_y)) < radio_boton:
        print("Color Negro activado")
        colorLaser = 0, 0, 0

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
