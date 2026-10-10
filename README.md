# UrbanOS

Plataforma municipal para cuidar la infraestructura de la ciudad a partir de reportes y datos: baches, grietas, alumbrado, señales y más.

> **Estado:** Etapa 0 (cascarón). Casi todo son carpetas con su plan. El módulo que se construye primero es **deterioro vial**.

## Idea en una frase
Una cuadrilla graba una calle, la IA encuentra baches y grietas, y el municipio ve un mapa con tramos en verde, amarillo o rojo.

## Qué hay aquí
| Carpeta | Contenido |
|---|---|
| `backend/` | Django + DRF, una app por módulo |
| `ai-service/` | Servicio FastAPI que solo hace detección |
| `frontend/` | Panel web (React + Tailwind + Leaflet) |
| `mobile/` | App móvil (React Native + Expo) |
| `infra/` | Docker Compose y configuración |
| `ml/` | Entrenamiento y evaluación del modelo |
| `docs/` | Documentación (empieza por `docs/ESTADO_MODULOS.md`) |

## Cómo correrlo
Todavía no hay nada que correr. En el Paso 2 se agrega Docker y quedará así:

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up
```

## Documentación
- [Estado de módulos](docs/ESTADO_MODULOS.md)
- [Hoja de ruta](docs/ROADMAP.md)
- [Arquitectura](docs/ARQUITECTURA.md)
- [Decisiones](docs/DECISIONES.md)
- [Privacidad](docs/PRIVACIDAD.md)

## Equipo
José Eduardo Salazar (backend, IA) y Takamura (frontend, UX, infraestructura, CI/CD).
