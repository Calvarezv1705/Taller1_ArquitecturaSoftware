# E-commerce Chat IA (Taller 1)

API REST de e-commerce de zapatos con chat inteligente, implementada con **Clean Architecture**.

## Características

- Gestión de productos (listar, filtrar, consultar por ID).
- Chat conversacional con memoria por sesión.
- Persistencia con SQLite + SQLAlchemy.
- Integración con Google Gemini.
- Pruebas unitarias con pytest.
- Contenerización con Docker.

## Arquitectura

El proyecto está dividido en 3 capas:

- **Dominio**: entidades, reglas de negocio, contratos de repositorio.
- **Aplicación**: casos de uso y DTOs.
- **Infraestructura**: FastAPI, repositorios SQLAlchemy, base de datos y Gemini.

## Estructura del proyecto

```text
e-commerce-chat-ai/
├── src/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── tests/
├── data/
├── evidencias/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Requisitos

- Python 3.12+ (recomendado para evitar incompatibilidades de dependencias).
- Docker Desktop (opcional para ejecución con contenedores).
- API Key de Google Gemini.

## Configuración local

1. Crear entorno virtual:
	- `python3.12 -m venv .venv`
2. Activar entorno:
	- macOS/Linux: `source .venv/bin/activate`
3. Instalar dependencias:
	- `pip install -r requirements.txt`
4. Configurar variables de entorno:
	- Copiar `.env.example` a `.env`
	- Definir `GEMINI_API_KEY`

## Ejecutar la API

```bash
uvicorn src.infrastructure.api.main:app --reload --host 0.0.0.0 --port 8000
```

O con Makefile:

```bash
make run
```

Swagger: http://localhost:8000/docs

## Ejecutar con Docker

```bash
docker compose up --build
```

## Endpoints principales

- `GET /` : información general.
- `GET /health` : estado del servicio.
- `GET /products` : lista productos (filtros opcionales `brand` y `category`).
- `GET /products/{product_id}` : detalle por ID.
- `POST /chat` : enviar mensaje al asistente.
- `GET /chat/history/{session_id}` : historial de chat.
- `DELETE /chat/history/{session_id}` : limpiar historial.

## Ejemplo de request de chat

```json
{
  "session_id": "user123",
  "message": "Hola, busco zapatos para correr talla 42"
}
```

## Testing

```bash
pytest
```

O con Makefile:

```bash
make test
```

## Colección de requests para pruebas

Puedes usar [docs/requests.http](docs/requests.http) con la extensión REST Client de VS Code para ejecutar rápidamente los endpoints y tomar evidencias.
