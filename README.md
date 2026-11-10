# 🚗 Detector de Somnolencia y Fatiga para Conductor en Tiempo Real (OpenCV)

Sistema de visión por computador en tiempo real desarrollado en Python con **OpenCV** para la monitorización activa del conductor en cabina. El sistema analiza continuamente el estado de vigilia detectando dos indicadores biométricos primarios: **el cierre prolongado de los ojos (microsueños)** y **la pérdida de postura cefálica (cabeceo vertical e inclinación lateral)**, activando advertencias visuales, acústicas y registrando evidencias de incidentes.

---

## 📋 Tabla de Contenidos
1. [Motivación y Objetivos](#-motivación-y-objetivos)
2. [Arquitectura y Metodología](#-arquitectura-y-metodología)
3. [Principales Funciones de OpenCV Utilizadas](#-principales-funciones-de-opencv-utilizadas)
4. [Dificultades Encontradas y Soluciones Implementadas](#-dificultades-encontradas-y-soluciones-implementadas)
5. [Estructura del Proyecto y Requisitos](#-estructura-del-proyecto-y-requisitos)
6. [Instrucciones de Uso y Controles](#-instrucciones-de-uso-y-controles)

---

## 🎯 Motivación y Objetivos

La fatiga y las distracciones al volante constituyen una de las causas más frecuentes de accidentes de tráfico graves en autopistas y trayectos largos. Un **microsueño** de tan solo 1.5 a 2 segundos a 120 km/h implica recorrer más de 50 metros sin ningún control sobre el vehículo.

### Objetivos principales del proyecto:
- **Procesamiento ligero y sin hardware especializado:** Implementar una solución eficiente en tiempo real capaz de ejecutarse en ordenadores portátiles o sistemas embebidos mediante una simple cámara web o cámara de salpicadero.
- **Detección robusta de ojos cerrados:** Identificar el parpadeo natural frente al cierre involuntario prolongado de párpados mediante análisis temporal amortiguado.
- **Detección de cabeceo e inclinación:** Detectar la pérdida de tono muscular en cuello mediante el descenso del centro facial respecto a un punto de calibración y el cálculo trigonométrico del ángulo ocular o rotación de la cabeza.
- **Sistema de respuesta y alerta inmediata:** Desencadenar alarmas visuales llamativas, señales acústicas y persistencia de fotogramas de evidencia para auditoría o registro de seguridad.

---

## 🧠 Arquitectura y Metodología

El desarrollo del sistema se articuló de manera incremental en cuatro fases:

1. **Fase 1 - Detección Facial Base:**
   - Detección de rostros en tiempo real mediante clasificadores en cascada de Haar (`haarcascade_frontalface_default.xml`).
   - Filtrado de ruido por umbral de área mínima (`area_min_cara = 8000`).
2. **Fase 2 - Análisis de Ojos y Filtrado Anatómico:**
   - Aislamiento de la región de interés (ROI) en la franja anatómica exacta de los ojos (del 26% al 60% de la altura facial, descartando cejas y boca).
   - Uso del clasificador especializado `haarcascade_eye_tree_eyeglasses.xml` (que funcionaba mejor que `haarcascade_eye.xml`) con restricciones proporcionales de tamaño mínimo y máximo (`minSize` y `maxSize`).
   - Contador temporal con histéresis/amortiguación para evitar falsos positivos producidos por parpadeos o destellos momentáneos.
3. **Fase 3 - Análisis Postural (Cabeceo vertical e inclinación lateral):**
   - **Cabeceo vertical:** Calibración de la altura base ($Y_{ref}$) del conductor en postura erguida mediante la tecla `c`. Si el centroide facial desciende más de un 25% de la altura de la cara respecto a su cota normal, se registra cabeceo por pérdida de tono muscular al quedarse dormido.
   - **Inclinación lateral (ladeo):** Cálculo trigonométrico del ángulo euclídeo de la recta que une los centros de ambos ojos ($\theta = |\arctan2(\Delta y, \Delta x)|$). Si la inclinación supera los $15^\circ$, se registra balanceo o ladeo de cabeza.
4. **Fase 4 - Protocolo de Alarma Multimodal:**
   - **Visual:** Marco perimetral rojo parpadeante y advertencias de gran visibilidad centradas en la parte inferior de la ventana.
   - **Acústica:** Generación de pitidos intermitentes de alta frecuencia (2500 Hz) que alertan al conductor sin bloquear el hilo principal de captura.
   - **Registro de Evidencia:** Guardado automático del fotograma crítico en la carpeta `ss_alarma/` al producirse cada nuevo episodio de sueño.

---

## 🛠️ Principales Funciones de OpenCV Utilizadas

En cumplimiento con los contenidos prácticos de la asignatura, el proyecto integra las siguientes funciones clave de la biblioteca OpenCV (`cv2`):

| Función OpenCV | Módulo / Clase de referencia | Descripción y Aplicación en el Proyecto |
|---|---|---|
| `cv2.VideoCapture()`, `read()`, `release()` | *8ª y 9ª Clase* | Inicialización, lectura continua de frames a 30 FPS y liberación del hardware de vídeo. |
| `cv2.flip()` | *1ª y 8ª Clase* | Reflejo horizontal (efecto espejo) para prueba intuitiva del usuario e inversión de frame para búsqueda de perfiles opuestos. |
| `cv2.cvtColor()` | *1ª, 4ª y 10ª Clase* | Transformaciones de color: `COLOR_BGR2GRAY` para procesar clasificadores Haar y `COLOR_BGR2HSV` para la corrección de iluminación. |
| `cv2.split()`, `cv2.merge()` | *1ª, 4ª y 10ª Clase* | Descomposición y recombinación de canales HSV para aumentar el canal de valor (`V`) dinámicamente mediante la barra de desplazamiento. |
| `cv2.CascadeClassifier()` | *7ª y 10ª Clase* | Carga de modelos pre-entrenados en XML: `haarcascade_frontalface_default.xml`, `haarcascade_profileface.xml` y `haarcascade_eye_tree_eyeglasses.xml`. |
| `detectMultiScale()` | *7ª y 10ª Clase* | Detección multiescala de objetos con ajuste de `scaleFactor`, `minNeighbors`, `minSize` y `maxSize`. |
| `cv2.rectangle()`, `cv2.circle()`, `cv2.line()` | *2ª y 7ª Clase* | Dibujo de primitivas gráficas: delimitador del rostro, centros oculares, vector de alineación ocular, línea de cabeceo y marco de alarma. |
| `cv2.putText()`, `cv2.getTextSize()` | *2ª Clase* | Renderizado de textos de estado y cálculo de dimensiones para centrar dinámicamente los avisos de emergencia en pantalla. |
| `cv2.namedWindow()`, `cv2.createTrackbar()` | *2ª y 10ª Clase* | Creación de interfaz gráfica con barra interactiva de control de brillo en tiempo real. |
| `cv2.imwrite()` | *1ª, 8ª y 11ª Clase* | Persistencia automática en disco de fotogramas de evidencia al dispararse la alarma en la carpeta `ss_alarma/`. |
| `cv2.imshow()`, `cv2.waitKey()`, `cv2.destroyAllWindows()` | *1ª a 11ª Clase* | Renderizado interactivo en ventana y captura de eventos de teclado (`c` para calibrar, `q` para salir). |

---

## 🔍 Dificultades Encontradas y Soluciones Implementadas

Durante el desarrollo e iteración del proyecto surgieron varios desafíos técnicos típicos de visión artificial basada en clasificadores clásicos de Haar:

1. **Falsos positivos y parpadeo intermitente del contador de ojos:**
   - *Problema:* Al cerrar los ojos, la sombra proyectada por las pestañas o pliegues de los párpados era interpretada en fotogramas aislados como un ojo abierto, provocando que un contador simple volviera a `0` y nunca alcanzara el umbral de alarma.
   - *Solución:* Implementación de un **acumulador amortiguado** (sube de 1 en 1 si no hay ojos, decrece lentamente si detecta 1 ojo sospechoso y solo reduce de forma rápida ante 2 ojos abiertos claros) y adopción del clasificador especializado `haarcascade_eye_tree_eyeglasses.xml`.
2. **Pérdida de la cara en giros y movimientos bruscos:**
   - *Problema:* El clasificador frontal estándar pierde la detección en cuanto el conductor gira la cabeza más de 15-20° o en movimientos rápidos.
   - *Solución:* Integración en cascada del clasificador de perfil (`haarcascade_profileface.xml`), volteo horizontal para cubrir ambos sentidos de giro, y una **memoria de persistencia temporal** (mantiene la última posición conocida durante 5 frames si se pierde momentáneamente).
3. **Inclinación lateral acusada (Limitación de Haar):**
   - *Qué no funcionó:* Intentamos evaluar caídas de cabeza muy acusadas hacia el hombro ($> 20^\circ$). Sin embargo, los clasificadores de Haar (Viola & Jones) no son invariantes a la rotación al basarse en patrones de contraste rectangulares ortogonales. Si el conductor ladea la cabeza excesivamente, el clasificador pierde el rostro por completo en vez de medir el ángulo.
   - *Cómo se abordó:* El sistema combina el **cabeceo vertical** (descenso de la coordenada $Y$ respecto a la línea de calibración con la tecla `c`, que resulta muy fiable en cabezadas de sueño) con el cálculo angular entre los ojos ($\arctan2$) mientras los ojos siguen en encuadre, documentando la rotación extrema fuera de eje como una limitación intrínseca de Haar.
4. **Falsas detecciones de ojos en nariz o boca:**
   - *Problema:* Si se busca en todo el rostro, las comisuras de los labios o fosas nasales pueden responder como ojos.
   - *Solución:* Recorte restrictivo de la ROI a la franja anatómica situada estrictamente entre el 26% y el 60% de la altura facial.

---

## 📁 Estructura del Proyecto y Requisitos

### Requisitos del entorno:
- Python 3.8+
- OpenCV (`opencv-python` o entorno de la asignatura)
- Biblioteca estándar de Python: `os`, `math`, `winsound` (Windows)

### Estructura de carpetas recomendada:
```
Programas/
├── haarcascades/
│   ├── haarcascade_frontalface_default.xml
│   ├── haarcascade_profileface.xml
│   └── haarcascade_eye_tree_eyeglasses.xml (o haarcascade_eye.xml)
└── Detector de Somnolencia (OpenCV)/
    ├── proyecto.py              # Script principal ejecutable
    ├── README.md                # Documentación del proyecto
    └── ss_alarma/               # Capturas automáticas de las alarmas (creado automáticamente)
```

---

## 🚀 Instrucciones de Uso y Controles

1. Conectar la cámara web y abrir una terminal en la carpeta del proyecto.
2. Ejecutar el script principal:
   ```bash
   python proyecto.py
   ```
3. **Controles en tiempo de ejecución:**
   - **Tecla `c`:** Calibra la altura erguida de referencia del conductor (pulsar sentado en la posición habitual de conducción).
   - **Barra 'Brillo':** Permite regular el brillo de la imagen mediante ecualización en canal V (HSV) si las condiciones de luz en cabina son tenues.
   - **Tecla `q`:** Cierra la aplicación y libera los recursos de la cámara.
