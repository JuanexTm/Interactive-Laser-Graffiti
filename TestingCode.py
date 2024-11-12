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
        video = cv2.VideoCapture('Assets/idle.mp4')
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
button_size = (160, 160)

# Carga de imágenes con el nuevo sistema de respaldo
icon_red = cargar_imagen_segura('Assets/Sprays/redSpray.png', button_size)
icon_yellow = cargar_imagen_segura('Assets/Sprays/yellowSpray.png', button_size)
icon_green = cargar_imagen_segura('Assets/Sprays/greenSpray.png', button_size)
icon_blue = cargar_imagen_segura('Assets/Sprays/blueSpray.png', button_size)
icon_lila = cargar_imagen_segura('Assets/Sprays/purpleSpray.png', button_size)
icon_pink = cargar_imagen_segura('Assets/Sprays/pinkSpray.png', button_size)
icon_white = cargar_imagen_segura('Assets/Sprays/whiteSpray.png', button_size)

icon_red_selected = cargar_imagen_segura('Assets/SpraysSelected/redSpraySelected.png', button_size)
icon_yellow_selected = cargar_imagen_segura('Assets/SpraysSelected/yellowSpraySelected.png', button_size)
icon_green_selected = cargar_imagen_segura('Assets/SpraysSelected/greenSpraySelected.png', button_size)
icon_blue_selected = cargar_imagen_segura('Assets/SpraysSelected/blueSpraySelected.png', button_size)
icon_lila_selected = cargar_imagen_segura('Assets/SpraysSelected/purpleSpraySelected.png', button_size)
icon_pink_selected = cargar_imagen_segura('Assets/SpraysSelected/pinkSpraySelected.png', button_size)
icon_white_selected = cargar_imagen_segura('Assets/SpraysSelected/whiteSpraySelected.png', button_size)

# Crear un diccionario para mapear los íconos normales y seleccionados
iconos_estado = {
    'Rojo': {'normal': icon_red, 'selected': icon_red_selected},
    'Amarillo': {'normal': icon_yellow, 'selected': icon_yellow_selected},
    'Verde': {'normal': icon_green, 'selected': icon_green_selected},
    'Azul': {'normal': icon_blue, 'selected': icon_blue_selected},
    'Lila': {'normal': icon_lila, 'selected': icon_lila_selected},
    'Rosa': {'normal': icon_pink, 'selected': icon_pink_selected},
    'Blanco': {'normal': icon_white, 'selected': icon_white_selected}
}

reset_button_size = (90, 90)  # Ajusta estos valores según el tamaño que desees
slider_button_size = (84, 100)  # Ajusta para el botón del slider
slider_size = (80, 560)  # Ajusta para el rango del slider
slider_width = 20  # Ancho del área activa del slider

# Cargar los nuevos íconos
icon_reset = cargar_imagen_segura('Assets/resetButton.png', reset_button_size)
icon_eraser = cargar_imagen_segura('Assets/eraserButton.png', reset_button_size)
icon_slider_button = cargar_imagen_segura('Assets/sliderButton.png', slider_button_size)
icon_slider = cargar_imagen_segura('Assets/slider.png', slider_size)

if icon_slider_button is None:
    print("Error: No se pudo cargar el botón del slider")
else:
    print(f"Botón del slider cargado correctamente. Tamaño: {icon_slider_button.shape}")
    
# Variable para rastrear el color actualmente seleccionado
color_seleccionado = None

# Inicialización de botones de color y posiciones
colores_botones = [
    ((255, 0, 0), 'Azul', icon_blue), ((0, 0, 255), 'Rojo', icon_red),
    ((255, 90, 160), 'Lila', icon_lila), ((0, 255, 255), 'Amarillo', icon_yellow),
    ((0, 255, 0), 'Verde', icon_green), ((255, 0, 255), 'Rosa', icon_pink),
    ((255, 255, 255), 'Blanco', icon_white)
]

# Configuración de botones
botones = []
altura_botones = int(cap.get(4) - button_size[1])  # Ajustado para dar espacio al botón
ancho_frame = int(cap.get(3))
espaciado = ancho_frame // (len(colores_botones) + 1)

for i, (color, nombreColor, nombreIcono) in enumerate(colores_botones):
    x_pos = espaciado * (i + 1) - button_size[0] // 2
    botones.append((color, (x_pos, altura_botones), nombreColor, nombreIcono))


# btn_Reset = (ancho_frame - 60, int(cap.get(4) // 8))
# btn_Borrar = (ancho_frame - 60, int(cap.get(4) * 2 // 8))

# Actualizar la posición del botón reset a la esquina inferior derecha
def actualizar_posicion_reset(frame_width, frame_height):
    return (frame_width - reset_button_size[0] - 10, frame_height - reset_button_size[1] - 10)

# Función para verificar si un punto está en zona prohibida
def esta_en_zona_prohibida(punto, frame_width, frame_height, button_size):
    x, y = punto
    
    # Zona inferior (área de botones de colores)
    altura_botones = int(frame_height - button_size[1] - 10)
    if y > altura_botones:
        return True
    
    # Zona izquierda (área del slider)
    zona_slider_ancho = 120  # Ancho de la zona prohibida para el slider
    if x < zona_slider_ancho:
        return True
        
    return False

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

spraySfx = pygame.mixer.Sound("Assets/spray.mp3")

# # Parámetros del temporizador
# tiempo_total = 320  # 90 segundos
# tiempo_restante = tiempo_total
# start_time = None  # Momento en que se empieza a pintar
# tiempo_terminado = None

# # Parámetros de la barra de pintura
# barra_ancho_total = cap.get(3) - 100  # Ancho total de la barra
# barra_alto = 20  # Alto de la barra
# barra_x = 50  # Posición X de la barra
# barra_y = int(cap.get(4) - 10)  # Posición Y de la barra, debajo de los botones

# ============================================= Temporizador y barra =====================================================
# def dibujar_barra_pintura(frame, tiempo_restante):
#     # Calculamos el ancho proporcional de la barra basado en el tiempo restante
#     ancho_barra = int((tiempo_restante / tiempo_total) * barra_ancho_total)
    
#     # Asegurarnos de que las coordenadas sean enteros
#     cv2.rectangle(frame, (int(barra_x), int(barra_y)), (int(barra_x + barra_ancho_total), int(barra_y + barra_alto)), (255, 255, 255), 2)
    
#     # Dibujar la barra que representa la pintura restante
#     if ancho_barra > 0:
#         cv2.rectangle(frame, (int(barra_x), int(barra_y)), (int(barra_x + ancho_barra), int(barra_y + barra_alto)), (0, 255, 0), -1)


# ============================================= Actualización del tiempo =================================================
# def actualizar_tiempo():
#     global start_time, tiempo_restante
#     if laser_activo and colorElegido is True and colorLaser is not (0,0,0):
#         if start_time is None:
#             # Si empezamos a pintar, registramos el tiempo de inicio
#             start_time = time.time()
#         else:
#             # Calculamos cuánto tiempo ha pasado desde que se empezó a pintar
#             tiempo_pasado = time.time() - start_time
#             start_time = time.time()  # Actualizamos el tiempo de inicio para la siguiente vez
#             tiempo_restante -= tiempo_pasado  # Reducimos el tiempo restante
#             tiempo_restante = max(tiempo_restante, 0)  # No dejamos que el tiempo sea negativo


#     else:
#         # Si no estamos pintando, pausamos el temporizador
#         start_time = None

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

        # Verificar si el punto está en zona prohibida antes de dibujar
        if not esta_en_zona_prohibida(punto_actual, int(cap.get(3)), int(cap.get(4)), button_size):
            if laser_activo and ultimo_punto is not None and colorElegido and hayPintura:
                # Solo dibujar si el punto anterior también está fuera de la zona prohibida
                if not esta_en_zona_prohibida(ultimo_punto, int(cap.get(3)), int(cap.get(4)), button_size):
                    cv2.line(grafiti, ultimo_punto, punto_actual, (colorLaser), tamaño_trazo)
            
            ultimo_punto = punto_actual
        else:
            ultimo_punto = None  # Resetear el último punto si estamos en zona prohibida
            
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
    # if not mostrando_idle:
    #     # Actualizar tiempo y dibujar barra de pintura
    #     actualizar_tiempo()
    #     dibujar_barra_pintura(combined, tiempo_restante)

    #     if tiempo_restante == 0:
    #         hayPintura = False
    #         spraySfx.stop()
    #         tiempo_terminado = True


    # Actualizar el tiempo si el láser está pintando
    # actualizar_tiempo()

    # Dibujar la barra de pintura
    # dibujar_barra_pintura(frame, tiempo_restante)

    # if tiempo_restante == 0:
    #     hayPintura = False
    #     spraySfx.stop()
    #     tiempo_terminado = True
        
        


# ============================================ Botones ===================================================

    for color, (x, y), nombreColor, nombreIcono in botones:
        try:
            # Verificar que las coordenadas están dentro de los límites del frame
            if (y >= 0 and y + button_size[1] <= combined.shape[0] and 
                x >= 0 and x + button_size[0] <= combined.shape[1]):
                
            # Determinar qué ícono usar basado en si está seleccionado
                icono_a_usar = iconos_estado[nombreColor]['selected'] if nombreColor == color_seleccionado else iconos_estado[nombreColor]['normal']
                
                # Superponer el ícono correspondiente
                combined = superponer_imagen_con_alpha(combined, icono_a_usar, (x, y))
                
                # Verificar si el láser está sobre el botón
                if distancia(maxLoc, (x + button_size[0]//2, y + button_size[1]//2)) < radio_boton:
                    colorElegido = True
                    colorLaser = color
                    # Actualizar el color seleccionado
                    if color_seleccionado != nombreColor:
                        color_seleccionado = nombreColor
                        print(f"Color {nombreColor} activado")
                    
        except Exception as e:
            print(f"Error al dibujar botón {nombreColor}: {e}")
            continue

    radio_boton = 35
    
    # Actualizar la posición del botón reset
    btn_Reset = actualizar_posicion_reset(int(cap.get(3)), int(cap.get(4)))
    
    # Dibujar el botón reset en su nueva posición
    reset_x = btn_Reset[0]
    reset_y = btn_Reset[1]
    combined = superponer_imagen_con_alpha(combined, icon_reset, (reset_x, reset_y))
    if distancia(maxLoc, btn_Reset) < radio_boton:
        print("Canvas borrado")
        colorElegido = False
        grafiti = np.zeros_like(combined)
        laser_activo = False
        color_seleccionado = None 
        spraySfx.stop()
    # # Botón de borrar
    # eraser_x = btn_Borrar[0] - reset_button_size[0]//2
    # eraser_y = btn_Borrar[1] - reset_button_size[1]//2
    # combined = superponer_imagen_con_alpha(combined, icon_eraser, (eraser_x, eraser_y))
    # if distancia(maxLoc, btn_Borrar) < radio_boton:
    #     colorElegido = True
    #     print("Borrador activado")
    #     colorLaser = (0, 0, 0)


    # ============================================= Slider =====================================================

    # Dibujar el slider y su controlador
    top_y = int(center_y - slider_height / 2)
    bottom_y = int(center_y + slider_height / 2)

    # Dibujar el fondo del slider
    slider_background_x = slider_x - slider_width // 2
    slider_background_y = top_y
    combined = superponer_imagen_con_alpha(combined, icon_slider, (slider_background_x, slider_background_y))

    # Calcular la posición actual del botón deslizador
    slider_control_x = 30 + slider_x - slider_button_size[0] // 2

    # Comprobar si el láser está dentro del área del slider
    if slider_x - slider_button_size[0]//2 < maxLoc[0] < slider_x + slider_width + slider_button_size[0]//2 and \
    top_y < maxLoc[1] < bottom_y:
        slider_pos = maxLoc[1]
        tamaño_trazo = int(np.interp(slider_pos, [top_y, bottom_y], [slider_max, slider_min]))
        tamaño_trazo = max(slider_min, min(slider_max, tamaño_trazo))

    # Asegurar que slider_pos está inicializado
    if 'slider_pos' not in locals():
        slider_pos = center_y

    # Calcular la posición vertical del botón teniendo en cuenta su tamaño
    button_y = int(slider_pos - slider_button_size[1] // 2)

    # Asegurarse de que el botón no se salga de los límites del slider
    button_y = max(top_y, min(bottom_y - slider_button_size[1], button_y))

    # Dibujar el botón del slider
    if icon_slider_button is not None and isinstance(icon_slider_button, np.ndarray):
        try:
            # Asegurarse de que el botón tiene un canal alpha
            if icon_slider_button.shape[2] != 4:
                # Convertir a RGBA si no tiene canal alpha
                alpha = np.ones((*icon_slider_button.shape[:2], 1), dtype=np.uint8) * 255
                icon_slider_button = np.concatenate([icon_slider_button, alpha], axis=2)
            
            # Dibujar el botón del slider
            button_pos = (slider_control_x, button_y)
            combined = superponer_imagen_con_alpha(combined, icon_slider_button, button_pos)
        except Exception as e:
            print(f"Error al dibujar el botón del slider: {e}")
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
