# Detector de Somnolencia al Volante con OpenCV

Proyecto de visión por computador para detectar somnolencia y fatiga en un conductor en tiempo real mediante una cámara web. El sistema monitoriza el cierre prolongado de ojos (microsueños) y la inclinación de la cabeza (cabeceo vertical y ladeo), activando una alarma acústica y visual con captura de imagen ante situaciones de riesgo.

---

## Funcionamiento del sistema

El programa procesa el vídeo en tiempo real siguiendo estos pasos:

1. **Detección facial:** Localiza la cara del conductor mediante clasificadores Haar en escala de grises. Si el conductor gira la cabeza lateralmente, se utiliza el clasificador de perfil y una memoria temporal de 5 fotogramas para no perder la detección ante movimientos rápidos.
2. **Detección de ojos y microsueños:** Dentro de la cara, recorta la región de interés (ROI) correspondiente a los ojos (entre el 26% y el 60% de la altura facial). Utiliza el clasificador `haarcascade_eye_tree_eyeglasses.xml`. Si no detecta ojos abiertos durante más de 15 fotogramas seguidos (~1 segundo), se interpreta como microsueño. Se utiliza un acumulador con amortiguación para evitar que parpadeos normales o sombras en párpados reinicien la cuenta por error.
3. **Inclinación de la cabeza:**
   - **Cabeceo vertical:** Al iniciar o pulsar la tecla `c`, se calibra la altura normal de la cara en postura de conducción. Si la cabeza baja más de un 25% respecto a dicha referencia, se detecta una cabezada de sueño.
   - **Inclinación lateral:** Cuando ambos ojos son visibles, calcula el ángulo de la recta que los une mediante arcotangente (`atan2`). Si supera los 15 grados de inclinación, se considera ladeo por fatiga.
4. **Sistema de alarma:** Si se detecta cualquiera de los dos eventos de somnolencia, la pantalla parpadea en rojo, se emite un aviso sonoro intermitente mediante `winsound.Beep` y se guarda automáticamente un fotograma de la incidencia en la carpeta `ss_alarma/`.

---

## Funciones de OpenCV utilizadas

| Función | Clase | Uso en el proyecto |
|---|---|---|
| `cv2.VideoCapture()`, `read()`, `release()` | 8ª y 9ª Clase | Captura de vídeo desde la cámara en tiempo real y liberación del dispositivo. |
| `cv2.flip()` | 1ª y 8ª Clase | Modo espejo horizontal en la visualización e inversión para detectar perfil hacia ambos lados. |
| `cv2.cvtColor()` | 1ª, 4ª y 10ª Clase | Conversión a escala de grises (`COLOR_BGR2GRAY`) para los clasificadores Haar y a `COLOR_BGR2HSV` para el brillo. |
| `cv2.split()`, `cv2.merge()` | 1ª y 10ª Clase | Separación y unión de canales HSV para modificar el canal de valor (V) con la barra de brillo. |
| `cv2.CascadeClassifier()`, `detectMultiScale()` | 7ª y 10ª Clase | Carga y ejecución de los clasificadores Haar para cara frontal, perfil y ojos. |
| `cv2.rectangle()`, `cv2.circle()`, `cv2.line()` | 2ª y 7ª Clase | Dibujo del cuadro delimitador, centros de los ojos, línea de inclinación, línea límite de cabeceo y marco de alarma. |
| `cv2.putText()`, `cv2.getTextSize()` | 2ª Clase | Impresión de datos en pantalla y cálculo del tamaño del texto para centrar el mensaje de alerta. |
| `cv2.namedWindow()`, `cv2.createTrackbar()` | 2ª y 10ª Clase | Creación de la ventana principal y de la barra deslizante para regular el brillo si hay poca luz en cabina. |
| `cv2.imwrite()` | 1ª, 8ª y 11ª Clase | Guardado automático del fotograma de evidencia al activarse la alarma. |
| `cv2.imshow()`, `cv2.waitKey()`, `cv2.destroyAllWindows()` | 1ª a 11ª Clase | Muestra de la ventana en bucle, control de teclas (`c` y `q`) y cierre de ventanas al finalizar. |

---

## Problemas encontrados durante el desarrollo

- **Falsos positivos con ojos cerrados:** Al cerrar los ojos, las sombras de las pestañas o pliegues hacían que el clasificador detectara un falso ojo durante un único fotograma, reiniciando el contador a cero y evitando que saltara la alarma. Se solucionó cambiando al clasificador `haarcascade_eye_tree_eyeglasses.xml`, ajustando la ROI para excluir las cejas y usando un contador amortiguado (resta de forma gradual en vez de reiniciarse súbitamente).
- **Pérdida de cara al girar la cabeza:** El clasificador frontal estándar pierde la detección al girar ligeramente la cabeza. Se resolvió añadiendo `haarcascade_profileface.xml` (normal e invertido con `cv2.flip`) y un búfer de memoria que mantiene la última posición durante 5 fotogramas ante movimientos rápidos.
- **Inclinación lateral acusada:** Los clasificadores Haar se basan en patrones rectangulares y no son invariantes a la rotación. Si el conductor inclina la cabeza de forma extrema hacia el hombro (más de 20 grados), el clasificador deja de reconocer la cara. Por ello, la detección de cabeceo se apoya principalmente en el desplazamiento vertical (eje Y) y en el ángulo entre ojos mientras ambos son visibles.
- **Detección de ojos fuera de su posición:** Al buscar ojos en toda la cara se producían falsas detecciones en las comisuras de los labios o fosas nasales. Se solucionó restringiendo la búsqueda a la franja entre el 26% y el 60% de la altura de la cara.

---

## Requisitos y ejecución

- Python 3.x
- `opencv-python`
- Sistema operativo Windows (para la alarma sonora de `winsound`)

Para ejecutar el programa:

```bash
python proyecto.py
```

Controles:
- **`c`:** Calibra la altura normal de referencia de la cabeza (pulsar sentado en la posición habitual frente a la cámara).
- **Barra de brillo:** Ajusta la iluminación si la cámara capta una imagen oscura.
- **`q`:** Salir del programa.
