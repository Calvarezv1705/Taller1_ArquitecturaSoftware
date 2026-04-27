# 🛒 E-commerce Chat IA

API REST de e-commerce de zapatos con chat inteligente, implementada con **Clean Architecture** (3 capas).

**Universidad EAFIT** — Taller 1 de Arquitectura de Software  
**Autor:** Camilo Álvarez

---

## 📋 Descripción

Sistema de e-commerce que permite a los usuarios:

1. **Navegar productos** mediante endpoints REST tradicionales.
2. **Conversar con un asistente de IA** (Google Gemini) que les ayuda a encontrar el zapato perfecto.
3. El asistente **recuerda la conversación** (últimos 6 mensajes) para dar respuestas coherentes.

---

## 🚀 Tecnologías

| Tecnología | Propósito | Capa |
|---|---|---|
| **Python 3.12** | Lenguaje principal | Todas |
| **FastAPI** | Framework web para API REST | Infraestructura |
| **Pydantic** | Validación de datos (DTOs) | Aplicación |
| **SQLAlchemy** | ORM para base de datos | Infraestructura |
| **SQLite** | Base de datos ligera | Infraestructura |
| **Google Gemini** | IA conversacional | Infraestructura |
| **Docker** | Containerización | Deployment |
| **Pytest** | Testing unitario | Testing |

---

## 🏗️ Arquitectura

El proyecto sigue **Clean Architecture** con 3 capas independientes:

```
┌─────────────────────────────────────────────┐
│          INFRAESTRUCTURA (API, DB, IA)       │
│  FastAPI · SQLAlchemy · Google Gemini        │
├─────────────────────────────────────────────┤
│          APLICACIÓN (Casos de Uso)           │
│  ProductService · ChatService · DTOs         │
├─────────────────────────────────────────────┤
│          DOMINIO (Reglas de Negocio)          │
│  Product · ChatMessage · ChatContext          │
│  IProductRepository · IChatRepository         │
└─────────────────────────────────────────────┘
```

**Principios aplicados:**
- **Dependency Injection** — Los servicios reciben sus dependencias por constructor.
- **Repository Pattern** — Abstracción del acceso a datos mediante interfaces.
- **Service Layer** — Orquestación de la lógica de negocio en servicios.
- **DTOs** — Transferencia segura de datos entre capas con validación Pydantic.

---

## 📁 Estructura del Proyecto

```
e-commerce-chat-ai/
├── src/
│   ├── config.py                          # Configuración global
│   ├── domain/                            # 🔷 CAPA DE DOMINIO
│   │   ├── entities.py                    # Product, ChatMessage, ChatContext
│   │   ├── repositories.py               # IProductRepository, IChatRepository
│   │   └── exceptions.py                 # Excepciones de negocio
│   ├── application/                       # 🔶 CAPA DE APLICACIÓN
│   │   ├── dtos.py                        # DTOs con Pydantic
│   │   ├── product_service.py             # Servicio de productos
│   │   └── chat_service.py               # Servicio de chat con IA
│   └── infrastructure/                    # 🔸 CAPA DE INFRAESTRUCTURA
│       ├── api/
│       │   └── main.py                    # Endpoints FastAPI
│       ├── db/
│       │   ├── database.py                # Config SQLAlchemy
│       │   ├── models.py                  # Modelos ORM
│       │   └── init_data.py               # Datos semilla (10 productos)
│       ├── repositories/
│       │   ├── product_repository.py      # Impl. SQLAlchemy productos
│       │   └── chat_repository.py         # Impl. SQLAlchemy chat
│       └── llm_providers/
│           └── gemini_service.py          # Integración Google Gemini
├── tests/                                 # Pruebas unitarias
│   ├── conftest.py
│   ├── test_entities.py
│   ├── test_services.py
│   ├── test_dtos.py
│   └── test_exceptions.py
├── data/                                  # Base de datos (generada automáticamente)
├── evidencias/                            # Screenshots del taller
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## ⚙️ Requisitos Previos

- **Python 3.12+**
- **Docker Desktop** (para ejecución con contenedores)
- **API Key de Google Gemini** — obtener en https://aistudio.google.com/app/apikey

---

## 🔧 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/Calvarezv1705/Taller1_ArquitecturaSoftware.git
cd Taller1_ArquitecturaSoftware/e-commerce-chat-ai
```

### 2. Crear entorno virtual

```bash
python3.12 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y agrega tu API Key de Gemini:

```
GEMINI_API_KEY=tu_api_key_aqui
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
```

---

## ▶️ Ejecutar la API

### Ejecución local

```bash
uvicorn src.infrastructure.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Ejecución con Docker

```bash
docker compose up --build
```

### Acceder a la documentación

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **API Base:** http://localhost:8000

---

## 🔌 Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Información general de la API |
| `GET` | `/health` | Estado del servicio |
| `GET` | `/products` | Lista productos (filtros: `brand`, `category`) |
| `GET` | `/products/{id}` | Detalle de un producto |
| `POST` | `/chat` | Enviar mensaje al asistente IA |
| `GET` | `/chat/history/{session_id}` | Historial de una sesión |
| `DELETE` | `/chat/history/{session_id}` | Limpiar historial |

### Ejemplo de request de chat

```json
POST /chat
{
  "session_id": "user123",
  "message": "Hola, busco zapatos para correr talla 42"
}
```

**Respuesta:**

```json
{
  "session_id": "user123",
  "user_message": "Hola, busco zapatos para correr talla 42",
  "assistant_message": "¡Hola! Tengo varias opciones de running en talla 42...",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## 🧪 Testing

Ejecutar las pruebas unitarias:

```bash
pytest -v
```

El proyecto incluye **65 pruebas** organizadas en:

- `test_entities.py` — Validaciones y métodos de entidades del dominio
- `test_services.py` — Servicios de aplicación con mocks
- `test_dtos.py` — Validación de DTOs con Pydantic
- `test_exceptions.py` — Excepciones personalizadas del dominio

---

## 🐳 Docker

### Construir y ejecutar

```bash
docker compose up --build -d
```

### Ver logs

```bash
docker compose logs -f
```

### Detener

```bash
docker compose down
```

---

## 📸 Evidencias

Las capturas de pantalla se encuentran en la carpeta `evidencias/`:

| Archivo | Contenido |
|---------|-----------|
| `01-swagger-ui.png` | Swagger UI con todos los endpoints |
| `02-docker-logs.png` | Logs de Docker con la app corriendo |
| `03-docker-running.png` | Docker Desktop / `docker ps` |
| `04-api-call-products.png` | GET `/products` desde Postman |
| `05-api-call-chat.png` | POST `/chat` con respuesta de IA |
| `06-database.png` | SQLite con productos cargados |

---

## 👤 Autor

**Camilo Álvarez** — Universidad EAFIT
