# UrbanOS

**Plataforma municipal para cuidar la infraestructura de la ciudad con datos e inteligencia artificial.**

UrbanOS ayuda a un municipio a saber en qué estado están sus calles. Una persona toma una foto de un bache o una grieta, la app guarda dónde fue, una IA detecta el daño y todo se ve en un mapa donde cada tramo de calle aparece como **bueno, regular o malo**.



---


## Qué hace

- **Detecta daños en la calle** con visión por computadora: baches, grietas longitudinales, grietas transversales y piel de cocodrilo.
- **Ubica cada daño con GPS** y lo guarda para poder consultarlo después.
- **Muestra un mapa de deterioro por tramos** de calle, con colores y etiquetas (bueno, regular, malo).
- **Cuida la privacidad:** las fotos pueden mostrar rostros y placas, y el sistema está pensado para difuminarlos antes de guardar.

Usuarios previstos: operadores que capturan en la calle, ciudadanos que reportan, supervisores y administradores del municipio.

## Estado actual

| Parte | Carpeta | Estado |
|---|---|---|
| Backend (Django) | `backend/` | Proyecto base creado. Corre con SQLite y tiene `GET /api/salud/` y la documentación de la API. Apps `usuarios` y `deterioro` creadas, **sin modelos todavía** |
| App móvil (Expo) | `mobile/` | Base de diseño lista: tema, componentes y 5 pestañas. Las pantallas son provisionales y **todavía no se conectan al backend** |
| Servicio de IA (FastAPI) | `ai-service/` | Solo el entorno de Python. **Aún no tiene código** |
| Entrenamiento y evaluación | `ml/` | Entorno y carpetas listas para la actividad del curso (cuaderno de Colab) |
| Panel web (React) | `frontend/` | **Pendiente.** Lo desarrollará otra persona del equipo |
| Docker y automatización | `infra/`, `.github/` | **Pendiente** |

## Cómo funciona

```
 App móvil / Panel web  ──►  Backend (Django)  ──►  Base de datos
   (fotos y GPS)                  │
                                  ▼
                        Servicio de IA (FastAPI)
                        recibe una imagen y devuelve
                        los daños que encuentra
```

- El **backend** es el cerebro: guarda los datos, controla a los usuarios y decide qué hacer.
- El **servicio de IA** solo recibe una imagen y responde qué daños ve. No sabe nada de GPS ni de la base de datos.
- Al inicio la IA será una **versión simulada** para probar todo el flujo; el modelo real viene después y se medirá con métricas reales.

## Tecnologías

| Parte | Tecnologías |
|---|---|
| Backend | Python, Django, Django REST Framework, `drf-spectacular` (documentación de la API), `django-cors-headers`, `django-environ` |
| Base de datos | SQLite en desarrollo inicial. Se cambiará a PostgreSQL con PostGIS al agregar Docker |
| Servicio de IA | FastAPI, Uvicorn. Modelo de detección de objetos ajustado con el dataset RDD2022 (pendiente) |
| App móvil | React Native con Expo (SDK 57), TypeScript, Expo Router |
| Panel web | React (el resto del stack se define con quien lo desarrolle) |
| ML | Python, Jupyter, pandas, scikit-learn; Google Colab para los experimentos |

## Estructura del repositorio

```
urbanos/
├── backend/        # API en Django
├── ai-service/     # Servicio de detección con IA (FastAPI)
├── frontend/       # Panel web en React
├── mobile/         # App móvil (React Native + Expo)
├── ml/             # Notebooks, datos y scripts de entrenamiento y evaluación
├── infra/          # Docker y configuración (pendiente)
├── .github/        # Automatización con GitHub Actions (pendiente)
├── .env.example    # Variables de entorno de ejemplo
└── README.md
```

Cada carpeta tiene su propio entorno de dependencias, así que no se mezclan entre sí.

## Requisitos previos

| Herramienta | Para qué | Versión |
|---|---|---|
| Git | Control de versiones | Cualquiera reciente |
| Python | Backend, servicio de IA y ML | 3.x reciente (el mismo que usa todo el equipo) |
| Node.js | App móvil y panel web | **22.13.1**, indicada en `mobile/.nvmrc` |
| Expo Go | Probar la app móvil en tu teléfono | Última versión de la tienda |
| Android Studio | Emulador de Android (opcional) | Última versión |
| Xcode | Simulador de iPhone (opcional, **solo en Mac**) | Última versión |

> En **Windows** no se puede simular un iPhone. Puedes probar en Android o con Expo Go en un iPhone real.

## Cómo ejecutar cada parte

Los comandos se muestran para **Windows (PowerShell)** y para **Mac o Linux**. Parte siempre de la raíz del repositorio.

```bash
git clone https://github.com/E-SalazarDev/urbanos.git
cd urbanos
```

### Backend (Django)

```powershell
# Windows (PowerShell)
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
```

```bash
# Mac o Linux
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

Cuando arranque, comprueba que funciona:

- Estado del servidor: <http://127.0.0.1:8000/api/salud/> debe mostrar `{"estado":"ok","servicio":"urbanos-backend"}`
- Documentación de la API: <http://127.0.0.1:8000/api/docs/>

Notas:

- Es normal que `runserver` avise de "migraciones sin aplicar". **No corras `python manage.py migrate` todavía**: primero se define el modelo `Usuario` propio, y migrar antes complicaría ese cambio.
- Si aparece un error de PowerShell por permisos al activar el entorno, ejecuta una sola vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- Las variables de entorno se leen de un archivo `.env` en la raíz. Si no existe, el backend usa valores de desarrollo.

### App móvil (React Native + Expo)

```bash
cd mobile
npm install
cp .env.example .env     # en PowerShell: Copy-Item .env.example .env
npx expo start
```

Para verla:

1. Instala **Expo Go** en tu teléfono (Play Store o App Store).
2. El teléfono y la computadora deben estar en la **misma red Wi-Fi**.
3. Escanea el código QR: con la app Expo Go en Android, o con la cámara en iPhone.
4. Para el emulador de Android, presiona `a` en la terminal donde corre Expo.

Reglas para que el entorno funcione igual en Windows y en Mac:

- Instala paquetes nuevos con `npx expo install <paquete>`, no con `npm install`.
- No subas las carpetas `ios/` ni `android/`.
- Sube siempre `package-lock.json`.
- Si algo falla, corre `npx expo-doctor`.
- En un teléfono real, `localhost` no sirve: en `mobile/.env` usa la IP de tu computadora (por ejemplo `http://192.168.1.50:8000`). En el emulador de Android usa `http://10.0.2.2:8000`.

Más detalles en [`mobile/README.md`](mobile/README.md).

### Panel web (React)

> **Pendiente.** El proyecto todavía no existe; lo creará otra persona del equipo. Cuando esté listo, la idea es que se corra así:

```bash
cd frontend
npm install
npm run dev
```

El backend ya acepta peticiones desde `http://localhost:5173`, que es el puerto habitual de Vite. Si el panel usa otro puerto, hay que agregarlo a `CORS_ALLOWED_ORIGINS` en la configuración del backend. Quien cree el panel debe agregar aquí los comandos reales y un `README.md` dentro de `frontend/`.

### Servicio de IA (FastAPI)

> **Pendiente.** Hoy solo existe el entorno de Python. Preparar ese entorno:

```powershell
# Windows (PowerShell)
cd ai-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# Mac o Linux
cd ai-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Cuando exista el servicio, aquí se agregará el comando para arrancarlo.

### Entrenamiento y evaluación (ML)

La carpeta `ml/` contiene el trabajo de la actividad del curso: cuaderno de Google Colab, dataset, resultados y scripts de apoyo.

```bash
cd ml
python -m venv .venv          # en Mac o Linux: python3
# activar el entorno como en el backend, y luego:
pip install -r requirements.txt
```

Las librerías pesadas (PyTorch y Hugging Face) se instalan dentro de Google Colab, no en tu computadora.

## Hoja de ruta

| Etapa | Meta |
|---|---|
| 0 | Base del proyecto: repositorio ordenado, backend, servicio de IA simulado, Docker y documentación |
| 1 | **Foto con GPS → detección con IA → guardado → mapa**, funcionando de punta a punta |
| 2 | **Video → fotogramas → detecciones → mapa de deterioro por tramos** (verde, amarillo, rojo) |
| 3 | Territorio, tramos reales, detección de duplicados y reportes ciudadanos en la web |
| 4 | Órdenes de trabajo y cuadrillas; captura de video con GPS en la app |
| 5 | Versionado de modelos, automatización y monitoreo |
| 6 y 7 | Optimización de rutas, simulación, asistente y alumbrado y señales |

El enfoque actual son las **Etapas 0, 1 y 2**. Los demás módulos se crean cuando llegue su etapa, uno por uno.

## Cómo colaborar

- Rama principal: `main`. El trabajo va en ramas `feat/...` y `fix/...`, y se integra con Pull Request.
- Commits en español con el formato `tipo: descripción corta`, por ejemplo `feat: endpoint para listar detecciones`.
- Un commit por paso de trabajo.
- Nunca subas el archivo `.env`, bases de datos locales ni entornos virtuales. El `.gitignore` ya los excluye.
- Cada vez que se instale un paquete de Python, se actualiza el `requirements.txt` de esa carpeta con `pip freeze`.

## Equipo y licencia

**Equipo:** José Eduardo Salazar (backend, IA y datos) y Takamura (frontend, UX, infraestructura y CI/CD).

**Licencia:** por definir. Una nota para esa decisión: la librería YOLO de Ultralytics usa licencia AGPL-3.0. Para la escuela y el portafolio no hay problema, pero si algún día se vende a un municipio habrá que evaluar una alternativa con licencia más abierta o una licencia comercial.
