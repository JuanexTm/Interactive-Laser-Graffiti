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

btn_Reset = (ancho_frame - 50, int(cap.get(4) // 8))
btn_Borrar = (ancho_frame - 50, int(cap.get(4) * 2 // 8))


# Parámetros del slider
slider_min = 10  # Tamaño mínimo del trazo
slider_max = 50  # Tamaño máximo del trazo
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


    
# ============================================ Botones ===================================================

    for color, (x, y), nombreColor in botones:
        cv2.circle(frame, (x, y), radio_boton, color, -1)
        if distancia(maxLoc, (x, y)) < radio_boton:
            print(f"Color {nombreColor} activado")
            colorLaser = color

    # Botón de reset
    cv2.circle(frame, btn_Reset, radio_boton, (0, 0, 0), -1)
    if distancia(maxLoc, btn_Reset) < radio_boton:
        print("Canvas borrado")
        grafiti = np.zeros_like(frame)
        colorLaser = (0, 0, 0)

    # Botón de borrar
    cv2.circle(frame, btn_Borrar, radio_boton, (255, 255, 255), -1)
    if distancia(maxLoc, btn_Borrar) < radio_boton:
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
