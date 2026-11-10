import cv2
import os
import winsound
from math import atan2, degrees

color_verde = (0, 255, 0)
color_amarillo = (0, 255, 255)
color_rojo = (0, 0, 255)
color_referencia = (255, 0, 255)
color_texto = (255, 255, 255)

grosor = 2
fuente = cv2.FONT_HERSHEY_SIMPLEX
area_min_cara = 8000

frames_ojos_cerrados = 0
umbral_dormido = 15

frames_cabeza_inclinada = 0
umbral_cabeza = 15
angulo_max_lateral = 15
y_referencia = None

carpeta_alarma = 'ss_alarma'
if not os.path.exists(carpeta_alarma):
    os.makedirs(carpeta_alarma)

contador_alarma = 0
alarma_activa_previa = False
frames_en_alarma = 0

ultima_cara = None
frames_sin_cara = 0
max_frames_memoria = 5

incremento_brillo = 0

clasificador_caras = cv2.CascadeClassifier('../../haarcascades/haarcascade_frontalface_default.xml')
clasificador_ojos = cv2.CascadeClassifier('../../haarcascades/haarcascade_eye_tree_eyeglasses.xml')
clasificador_perfil = cv2.CascadeClassifier('../../haarcascades/haarcascade_profileface.xml')


def modifica_brillo(img):
    if incremento_brillo == 0:
        return img
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    limite = 255 - incremento_brillo
    v[v > limite] = 255
    v[v <= limite] += incremento_brillo
    hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def cambia_brillo(valor):
    global incremento_brillo
    incremento_brillo = valor


nombre_ventana = 'Detector de Somnolencia'
cv2.namedWindow(nombre_ventana)
cv2.createTrackbar('Brillo', nombre_ventana, 0, 100, cambia_brillo)

camara = cv2.VideoCapture(0)

if not camara.isOpened():
    print("No es posible abrir la cámara")
    exit()

while True:
    ret, frame = camara.read()
    if not ret:
        print("No es posible obtener la imagen")
        break

    frame = cv2.flip(frame, 1)
    alto_imagen, ancho_imagen, _ = frame.shape

    frame = modifica_brillo(frame)
    frame_byn = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    caras = clasificador_caras.detectMultiScale(frame_byn, 1.1, 3)

    caras_validas = []
    for (x, y, ancho, alto) in caras:
        if ancho * alto > area_min_cara:
            caras_validas.append((x, y, ancho, alto))

    if len(caras_validas) == 0:
        perfiles = clasificador_perfil.detectMultiScale(frame_byn, 1.1, 3)
        for (x, y, ancho, alto) in perfiles:
            if ancho * alto > area_min_cara:
                caras_validas.append((x, y, ancho, alto))

        if len(caras_validas) == 0:
            frame_byn_inv = cv2.flip(frame_byn, 1)
            perfiles_inv = clasificador_perfil.detectMultiScale(frame_byn_inv, 1.1, 3)
            for (x_inv, y, ancho, alto) in perfiles_inv:
                if ancho * alto > area_min_cara:
                    x_real = ancho_imagen - x_inv - ancho
                    caras_validas.append((x_real, y, ancho, alto))

    if len(caras_validas) > 0:
        cara_detectada = caras_validas[0]
        ultima_cara = cara_detectada
        frames_sin_cara = 0
    elif ultima_cara is not None and frames_sin_cara < max_frames_memoria:
        cara_detectada = ultima_cara
        frames_sin_cara += 1
    else:
        cara_detectada = None

    if cara_detectada is not None:
        x, y, ancho, alto = cara_detectada
        centro_cara_x = x + int(ancho / 2)
        centro_cara_y = y + int(alto / 2)

        if y_referencia is None:
            y_referencia = centro_cara_y

        y_limite_caida = y_referencia + int(alto * 0.25)

        cv2.line(frame, (0, y_limite_caida), (ancho_imagen, y_limite_caida), color_referencia, 1)
        cv2.putText(frame, "Limite cabeceo ('c' recalibrar)", (10, y_limite_caida - 5), fuente, 0.5, color_referencia, 1)
        cv2.circle(frame, (centro_cara_x, centro_cara_y), 4, color_referencia, -1)

        y_ini = max(0, y + int(alto * 0.26))
        y_fin = min(alto_imagen, y + int(alto * 0.60))
        x_ini = max(0, x + int(ancho * 0.12))
        x_fin = min(ancho_imagen, x + int(ancho * 0.88))

        roi_ojos_byn = frame_byn[y_ini:y_fin, x_ini:x_fin]

        tam_min_ojo = (int(ancho * 0.13), int(alto * 0.09))
        tam_max_ojo = (int(ancho * 0.35), int(alto * 0.25))

        ojos = clasificador_ojos.detectMultiScale(
            roi_ojos_byn,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=tam_min_ojo,
            maxSize=tam_max_ojo
        )

        centros_ojos = []
        for (x1, y1, ancho1, alto1) in ojos:
            radio = int((ancho1 + alto1) / 4)
            centro_ojo = (x_ini + x1 + radio, y_ini + y1 + radio)
            centros_ojos.append(centro_ojo)
            cv2.circle(frame, centro_ojo, radio, color_amarillo, grosor)

        if len(ojos) == 0:
            frames_ojos_cerrados = min(umbral_dormido + 10, frames_ojos_cerrados + 1)
        elif len(ojos) == 1:
            frames_ojos_cerrados = max(0, frames_ojos_cerrados - 1)
        else:
            frames_ojos_cerrados = max(0, frames_ojos_cerrados - 3)

        cabeza_caida = (centro_cara_y > y_limite_caida)
        cabeza_ladeada = False
        angulo_ojos = 0.0

        if len(centros_ojos) >= 2:
            centros_ojos.sort(key=lambda p: p[0])
            ojo_izq = centros_ojos[0]
            ojo_der = centros_ojos[-1]

            dx = ojo_der[0] - ojo_izq[0]
            dy = ojo_der[1] - ojo_izq[1]

            if dx > int(ancho * 0.20):
                cv2.line(frame, ojo_izq, ojo_der, color_amarillo, 2)
                angulo_ojos = abs(degrees(atan2(dy, dx)))
                if angulo_ojos > angulo_max_lateral:
                    cabeza_ladeada = True

        if cabeza_caida or cabeza_ladeada:
            frames_cabeza_inclinada = min(umbral_cabeza + 10, frames_cabeza_inclinada + 1)
        else:
            frames_cabeza_inclinada = max(0, frames_cabeza_inclinada - 2)

        alerta_ojos = (frames_ojos_cerrados >= umbral_dormido)
        alerta_cabeza = (frames_cabeza_inclinada >= umbral_cabeza)
        en_alarma = (alerta_ojos or alerta_cabeza)

        if en_alarma:
            color_estado = color_rojo
            frames_en_alarma += 1

            if alerta_ojos and alerta_cabeza:
                texto_estado = "DORMIDO (Ojos y Cabeza)"
                mensaje_alerta = "PELIGRO: CONDUCTOR DORMIDO!"
            elif alerta_ojos:
                texto_estado = "DORMIDO (Ojos cerrados)"
                mensaje_alerta = "ALERTA: OJOS CERRADOS!"
            else:
                texto_estado = "DORMIDO (Cabeza inclinada)"
                mensaje_alerta = "ALERTA: CABEZA INCLINADA!"

            if frames_en_alarma % 2 == 0:
                cv2.rectangle(frame, (0, 0), (ancho_imagen - 1, alto_imagen - 1), color_rojo, 12)

            (ancho_texto, alto_texto), _ = cv2.getTextSize(mensaje_alerta, fuente, 0.9, 3)
            pos_x = int((ancho_imagen - ancho_texto) / 2)
            pos_y = int(alto_imagen - 25)
            cv2.putText(frame, mensaje_alerta, (pos_x, pos_y), fuente, 0.9, color_rojo, 3)

            if frames_en_alarma % 8 == 1:
                winsound.Beep(2500, 120)

            if not alarma_activa_previa:
                contador_alarma += 1
                ruta_foto = carpeta_alarma + '/alarma_' + str(contador_alarma) + '.jpg'
                cv2.imwrite(ruta_foto, frame)
                print("Alarma guardada en:", ruta_foto)
                alarma_activa_previa = True

        elif frames_ojos_cerrados > 0 or frames_cabeza_inclinada > 0:
            color_estado = color_amarillo
            alarma_activa_previa = False
            frames_en_alarma = 0
            texto_estado = "Ojos: " + str(frames_ojos_cerrados) + "/" + str(umbral_dormido) + " | Cabeza: " + str(frames_cabeza_inclinada) + "/" + str(umbral_cabeza)
        else:
            color_estado = color_verde
            alarma_activa_previa = False
            frames_en_alarma = 0
            texto_estado = "DESPIERTO (Inclinacion: " + str(int(angulo_ojos)) + " deg)"

        cv2.rectangle(frame, (x, y), (x + ancho, y + alto), color_estado, grosor)
        cv2.putText(frame, texto_estado, (x, y - 10), fuente, 0.6, color_estado, grosor)

    else:
        cv2.putText(frame, "Cara no detectada", (10, 65), fuente, 0.7, color_amarillo, 2)

    cv2.putText(frame, "'c' Calibrar | 'q' Salir | Alarmas: " + str(contador_alarma), (10, 30), fuente, 0.6, color_texto, 2)

    cv2.imshow(nombre_ventana, frame)

    tecla = cv2.waitKey(1)
    if tecla == ord('q'):
        break
    elif tecla == ord('c') and cara_detectada is not None:
        y_referencia = cara_detectada[1] + int(cara_detectada[3] / 2)

camara.release()
cv2.destroyAllWindows()
