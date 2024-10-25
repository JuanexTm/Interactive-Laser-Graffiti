import cv2
import numpy as np
import pygame
import time
import os

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

# Nuevas variables para el sistema de idle
tiempo_ultimo_laser = time.time()
tiempo_idle_limite = 25  # segundos antes de mostrar la animación
video_idle = None
mostrando_idle = False

def inicializar_video_idle():
    """Inicializa el video de idle"""
    try:
        video = cv2.VideoCapture('idle.mp4')
        if not video.isOpened():
            print("Error: No se pudo cargar el video de idle")
            return None
        return video
    except Exception as e:
        print(f"Error al cargar el video de idle: {e}")
        return None

def obtener_frame_idle(video):
    """Obtiene un frame del video idle y lo reinicia si es necesario"""
    if video is None:
        return None
        
    ret, frame = video.read()
    if not ret:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reiniciar el video
        ret, frame = video.read()
    
    return frame if ret else None

def cargar_imagen_segura(nombre_archivo, size):
    try:
        # Leer la imagen con el canal alfa (transparencia)
        imagen = cv2.imread(nombre_archivo, cv2.IMREAD_UNCHANGED)
        if imagen is None:
            # Si la imagen no se puede cargar, crear una imagen de color sólido
            imagen = np.ones((size[1], size[0], 4), dtype=np.uint8)
            if 'Red' in nombre_archivo:
                imagen[:] = (0, 0, 255, 255)
            elif 'Yellow' in nombre_archivo:
                imagen[:] = (0, 255, 255, 255)
            elif 'Green' in nombre_archivo:
                imagen[:] = (0, 255, 0, 255)
            elif 'Blue' in nombre_archivo:
                imagen[:] = (255, 0, 0, 255)
            elif 'Lila' in nombre_archivo:
                imagen[:] = (255, 90, 160, 255)
            elif 'Pink' in nombre_archivo:
                imagen[:] = (255, 0, 255, 255)
            elif 'White' in nombre_archivo:
                imagen[:] = (255, 255, 255, 255)
            return imagen

        # Redimensionar la imagen manteniendo el canal alfa
        if imagen.shape[2] == 4:
            # Redimensionar cada canal por separado para mantener la nitidez
            b, g, r, a = cv2.split(imagen)
            b = cv2.resize(b, size, interpolation=cv2.INTER_NEAREST)
            g = cv2.resize(g, size, interpolation=cv2.INTER_NEAREST)
            r = cv2.resize(r, size, interpolation=cv2.INTER_NEAREST)
            a = cv2.resize(a, size, interpolation=cv2.INTER_NEAREST)
            return cv2.merge([b, g, r, a])
        else:
            # Si no tiene canal alfa, agregar uno
            imagen_rgb = cv2.resize(imagen, size, interpolation=cv2.INTER_NEAREST)
            alpha = np.ones(size, dtype=np.uint8) * 255
            return cv2.merge([imagen_rgb, alpha])

    except Exception as e:
        print(f"Error al cargar {nombre_archivo}: {e}")
        imagen = np.ones((size[1], size[0], 4), dtype=np.uint8) * 128
        imagen[:, :, 3] = 255
        return imagen

def superponer_imagen_con_alpha(fondo, imagen_rgba, pos):
    try:
        x, y = pos
        if imagen_rgba.shape[2] == 4:  # Verificar que la imagen tiene canal alfa
            # Separar los canales
            alpha = imagen_rgba[:, :, 3] / 255.0
            foreground = imagen_rgba[:, :, :3]
            
            # Obtener la región del fondo
            h, w = foreground.shape[:2]
            background_region = fondo[y:y+h, x:x+w]
            
            # Crear matrices 3D de alpha para la operación
            alpha_3d = np.stack([alpha] * 3, axis=-1)
            
            # Realizar la mezcla
            for c in range(3):  # Para cada canal de color
                background_region[:, :, c] = background_region[:, :, c] * (1 - alpha) + foreground[:, :, c] * alpha
                
            # Asignar el resultado de vuelta al fondo
            fondo[y:y+h, x:x+w] = background_region
            
    except Exception as e:
        print(f"Error al superponer imagen: {e}")
    
    return fondo
    try:
        # Leer la imagen con el canal alfa (transparencia)
        imagen = cv2.imread(nombre_archivo, cv2.IMREAD_UNCHANGED)
        if imagen is None:
            # Si la imagen no se puede cargar, crear una imagen de color sólido
            imagen = np.ones((size[1], size[0], 3), dtype=np.uint8)
            if 'Red' in nombre_archivo:
                imagen[:] = (0, 0, 255)
            elif 'Yellow' in nombre_archivo:
                imagen[:] = (0, 255, 255)
            elif 'Green' in nombre_archivo:
                imagen[:] = (0, 255, 0)
            elif 'Blue' in nombre_archivo:
                imagen[:] = (255, 0, 0)
            elif 'Lila' in nombre_archivo:
                imagen[:] = (255, 90, 160)
            elif 'Pink' in nombre_archivo:
                imagen[:] = (255, 0, 255)
            elif 'White' in nombre_archivo:
                imagen[:] = (255, 255, 255)
            return cv2.resize(imagen, size)
        
        # Si la imagen tiene 4 canales (RGBA)
        if imagen.shape[2] == 4:
            # Separar los canales de color y el canal alfa
            alpha_channel = imagen[:, :, 3]
            rgb_channels = imagen[:, :, :3]

            # Crear una máscara normalizada del canal alfa
            alpha_mask = alpha_channel / 255.0

            # Extender la máscara para aplicarla a cada canal de color
            alpha_mask = np.stack([alpha_mask] * 3, axis=-1)

            # Aplicar la transparencia
            rgb_channels = rgb_channels.astype(float) * alpha_mask
            
            # Convertir de vuelta a uint8
            rgb_channels = rgb_channels.astype(np.uint8)

            # Redimensionar la imagen resultante
            return cv2.resize(rgb_channels, size)
        else:
            # Si la imagen no tiene canal alfa, simplemente redimensionarla
            return cv2.resize(imagen, size)

    except Exception as e:
        print(f"Error al cargar {nombre_archivo}: {e}")
        # Crear una imagen de respaldo
        imagen = np.ones((size[1], size[0], 3), dtype=np.uint8) * 128
        return imagen

# Tamaño de los botones
button_size = (116, 116)

# Carga de imágenes con el nuevo sistema de respaldo
icon_red = cargar_imagen_segura('colorRed.png', button_size)
icon_yellow = cargar_imagen_segura('colorYellow.png', button_size)
icon_green = cargar_imagen_segura('colorGreen.png', button_size)
icon_blue = cargar_imagen_segura('colorBlue.png', button_size)
icon_lila = cargar_imagen_segura('colorLila.png', button_size)
icon_pink = cargar_imagen_segura('colorPink.png', button_size)
icon_white = cargar_imagen_segura('colorWhite.png', button_size)

# Inicialización de botones de color y posiciones
colores_botones = [
    ((255, 0, 0), 'Azul', icon_blue), ((0, 0, 255), 'Rojo', icon_red),
    ((255, 90, 160), 'Lila', icon_lila), ((0, 255, 255), 'Amarillo', icon_yellow),
    ((0, 255, 0), 'Verde', icon_green), ((255, 0, 255), 'Rosa', icon_pink),
    ((255, 255, 255), 'Blanco', icon_white)
]

# Configuración de botones
botones = []
altura_botones = int(cap.get(4) - button_size[1] - 10)  # Ajustado para dar espacio al botón
ancho_frame = int(cap.get(3))
espaciado = ancho_frame // (len(colores_botones) + 1)

for i, (color, nombreColor, nombreIcono) in enumerate(colores_botones):
    x_pos = espaciado * (i + 1) - button_size[0] // 2
    botones.append((color, (x_pos, altura_botones), nombreColor, nombreIcono))


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
tiempo_total = 320  # 90 segundos
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

    if video_idle is None:
        video_idle = inicializar_video_idle()

    
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
        tiempo_ultimo_laser = time.time()  # Actualizar el tiempo del último láser detectado
        mostrando_idle = False  # Desactivar la animación idle
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

    
    # tiempo_sin_laser = time.time() - tiempo_ultimo_laser

    # Crear el frame base combinando la cámara y el grafiti
    combined = cv2.addWeighted(frame, 0.7, grafiti, 0.3, 0)

    # Si no estamos en idle, dibujamos toda la UI
    if not mostrando_idle:
        # Actualizar tiempo y dibujar barra de pintura
        actualizar_tiempo()
        dibujar_barra_pintura(combined, tiempo_restante)

        if tiempo_restante == 0:
            hayPintura = False
            spraySfx.stop()
            tiempo_terminado = True


    # Actualizar el tiempo si el láser está pintando
    actualizar_tiempo()

    # Dibujar la barra de pintura
    dibujar_barra_pintura(frame, tiempo_restante)

    if tiempo_restante == 0:
        hayPintura = False
        spraySfx.stop()
        tiempo_terminado = True
        
        


# ============================================ Botones ===================================================

    for color, (x, y), nombreColor, nombreIcono in botones:
        try:
            # Verificar que las coordenadas están dentro de los límites del frame
            if (y >= 0 and y + button_size[1] <= combined.shape[0] and 
                x >= 0 and x + button_size[0] <= combined.shape[1]):
                
                # Superponer el ícono usando la nueva función
                combined = superponer_imagen_con_alpha(combined, nombreIcono, (x, y))
                
                # Verificar si el láser está sobre el botón
                if distancia(maxLoc, (x + button_size[0]//2, y + button_size[1]//2)) < radio_boton:
                    colorElegido = True
                    colorLaser = color
                    print(f"Color {nombreColor} activado")
                    
        except Exception as e:
            print(f"Error al dibujar botón {nombreColor}: {e}")
            continue

    radio_boton = 35
    
    # Botón de reset
    cv2.circle(combined, btn_Reset, radio_boton, (0, 0, 0), -1)
    if distancia(maxLoc, btn_Reset) < radio_boton:
        print("Canvas borrado")
        colorElegido = False
        grafiti = np.zeros_like(combined)
        # colorLaser = (0, 0, 0)
        laser_activo = False

    # Botón de borrar
    cv2.circle(combined, btn_Borrar, radio_boton, (255, 255, 255), -1)
    if distancia(maxLoc, btn_Borrar) < radio_boton:
        colorElegido = True
        print("Borrador activado")
        colorLaser = (0, 0, 0)


    # ============================================= Slider =====================================================

    # Dibujar el área del slider centrada en el eje Y
    top_y = int(center_y - slider_height / 2)
    bottom_y = int(center_y + slider_height / 2)
    cv2.rectangle(combined, (slider_x, top_y), (slider_x + slider_width, bottom_y), (100, 100, 100), -1)

    # Dibujar el control del slider
    cv2.rectangle(combined, (slider_x, slider_pos - 10), (slider_x + slider_width, slider_pos + 10), (255, 255, 255), -1)

    # Comprobar si el láser está dentro del área del slider
    if slider_x < maxLoc[0] < slider_x + slider_width and top_y < maxLoc[1] < bottom_y:
        slider_pos = maxLoc[1]
        tamaño_trazo = int(np.interp(slider_pos, [top_y, bottom_y], [slider_max, slider_min]))

    # Mostrar el tamaño del trazo
    cv2.putText(combined, f'{tamaño_trazo}', (slider_x + 40, top_y - 10), cv2.FONT_ITALIC, 1, (255, 255, 255), 2)

    # ==================================================================================================

    # Comprobar si debemos mostrar la animación idle
    tiempo_sin_laser = time.time() - tiempo_ultimo_laser
    
    if tiempo_sin_laser >= tiempo_idle_limite:
        if not mostrando_idle:
            mostrando_idle = True
        
        # Obtener frame del video idle
        frame_idle = obtener_frame_idle(video_idle)
        if frame_idle is not None:
            # Redimensionar el frame idle al tamaño de la ventana
            frame_idle = cv2.resize(frame_idle, (combined.shape[1], combined.shape[0]))
            # Reemplazar completamente el frame combinado con el frame idle
            combined = frame_idle


    # if not mostrando_idle:
    #     combined = cv2.addWeighted(frame, 0.7, grafiti, 0.3, 0)
    # else:
    #     combined = frame


    # Mostrar el frame combinado
    cv2.imshow('Track Laser', combined)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
if video_idle is not None:
    video_idle.release()
cap.release()
cv2.destroyAllWindows()
