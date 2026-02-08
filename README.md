# Insurance Copilot AI

Aplicación de asistencia inteligente para cotización y consulta de seguros, potenciada por IA Generativa.

## 🚀 Características

- **Chat Inteligente**: Resuelve dudas sobre pólizas y condiciones legales usando RAG (Retrieval-Augmented Generation).
- **Cotizador de Seguros**: Calcula primas en tiempo real basado en el perfil del conductor y vehículo.
- **Gestión de Usuarios**: Registro y autenticación segura con JWT.
- **Arquitectura Moderna**: Backend FastAPI (Python) + Frontend Angular/React (según implementación) + PostgreSQL (pgvector).

## 📋 Requisitos Previos

- [Docker](https://www.docker.com/) y Docker Compose (Recomendado).
- Python 3.12+ (para ejecución local del backend).
- Node.js 20+ (para ejecución local del frontend).

## 🛠️ Configuración

1. **Clonar el repositorio**:
   ```bash
   git clone <URL_DEL_REPO>
   cd InsuranceCopilotAI
   ```

2. **Variables de Entorno**:
   Crea un archivo `.env` en la carpeta `backend/` basado en `.env.example`.
   Ejemplo básico:
   ```env
   # Backend
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_SERVER=db
   POSTGRES_PORT=5432
   POSTGRES_DB=insurance_copilot
   
   # IA
   OPENAI_API_KEY=sk-tu-api-key-aqui

   # Seguridad
   SECRET_KEY=tu-clave-secreta-segura
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## 🐳 Ejecución con Docker (Recomendado)

Levanta toda la infraestructura (Base de datos, Backend y Frontend) con un solo comando:

```bash
docker-compose up --build
```

- **Frontend**: http://localhost:80
- **Backend API Docs**: http://localhost:8000/docs
- **Base de Datos**: Puerto 5432

## 💻 Ejecución Local

### Backend (FastAPI)

1. Navega a `backend/`:
   ```bash
   cd backend
   ```
2. Instala dependencias:
   ```bash
   pip install .
   # O si usas poetry/env virtual manual
   pip install -r requirements.txt # si existe, o usar pyproject.toml
   ```
3. Ejecuta el servidor:
   ```bash
   uvicorn main:app --reload
   ```
   La API estará en `http://localhost:8000`.

### Frontend (Angular)

1. Navega a `frontend/insurance-copilot/`:
   ```bash
   cd frontend/insurance-copilot
   ```
2. Instala dependencias:
   ```bash
   npm install
   ```
3. Ejecuta el servidor de desarrollo:
   ```bash
   npm start
   ```
   La aplicación estará en `http://localhost:4200`.

## 🔐 Autenticación y Uso

### Registro de Usuario
Realiza una petición `POST` a `/api/v1/auth/register`:
```json
{
  "email": "usuario@ejemplo.com",
  "password": "password123",
  "username": "usuario1",
  "role": "viewer"
}
```

### Login
Realiza una petición `POST` a `/api/v1/auth/token` (Form-Data):
- `username`: usuario@ejemplo.com
- `password`: password123

Recibirás un `access_token` que debes incluir en los headers de las peticiones protegidas:
`Authorization: Bearer <tu_token>`

## 🧪 Endpoints Principales

- **Chat**: `POST /api/v1/chat` - Interactúa con el agente de seguros.
- **Cotizar**: `POST /api/v1/quotes/calculate` - Obtiene opciones de seguro.
- **Confirmar Cotización**: `POST /api/v1/quotes` - Guarda la selección del usuario.
