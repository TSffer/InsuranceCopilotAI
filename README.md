# Insurance Copilot AI

**Asistente Inteligente de Seguros Potenciado por RAG Avanzado y Agentes**

Insurance Copilot AI es una plataforma de última generación diseñada para revolucionar la interacción con pólizas y cotizaciones de seguros. Utiliza una arquitectura híbrida de **Retrieval-Augmented Generation (RAG)** y agentes autónomos para ofrecer respuestas precisas, contextuales y seguras.

---

## 🚀 Características Clave

### 🧠 Inteligencia Artificial Avanzada
- **RAG Híbrido (Hybrid Search)**: Combina búsqueda semántica (Vectores Densos con OpenAI) y búsqueda por palabras clave (Vectores Dispersos con SPLADE) para una recuperación de información inigualable.
- **Reranking Neural**: Utiliza **FlashRank** para reordenar los resultados de búsqueda y priorizar la información más relevante.
- **Memoria Persistente**: Recuerda el contexto de la conversación a través de múltiples sesiones gracias a **LangGraph** y **PostgreSQL**.
- **Guardrails Semánticos**: Protege contra alucinaciones y respuestas inseguras mediante capas de verificación.

### 💻 Arquitectura Moderna
- **Frontend**: Construido con **Angular 21+** y **Tailwind CSS v4** para una interfaz rápida, reactiva y estéticamente premium.
- **Backend**: API robusta y asíncrona desarrollada con **FastAPI** y **Python 3.12+**.
- **Vector Store**: **Qdrant** para el almacenamiento y búsqueda eficiente de embeddings.
- **Base de Datos**: **PostgreSQL** (con pgvector) para gestión de usuarios, historial y datos de negocio.

### 🛡️ Seguridad y Gestión
- **Autenticación JWT**: Sistema seguro de registro y login.
- **Gestión de Roles**: Control de acceso para usuarios y administradores.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
| :--- | :--- |
| **Frontend** | Angular 21, Tailwind CSS v4, ngx-markdown |
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **IA & LLM** | LangChain, LangGraph, OpenAI GPT-4o |
| **Vectores** | Qdrant, FastEmbed (SPLADE), FlashRank |
| **Base de Datos** | PostgreSQL, SQLAlchemy, AsyncPG |
| **Gestión Paquetes** | `uv` (Python), `npm` (Node.js) |
| **Infraestructura** | Docker, Docker Compose |

---

## 📋 Requisitos Previos

- [Docker](https://www.docker.com/) y Docker Compose.
- **Python 3.12+** (y [uv](https://github.com/astral-sh/uv) recomendado para gestión eficiente).
- **Node.js 20+**.

---

## 🚀 Instalación y Ejecución

### Opción A: Despliegue Completo con Docker (Recomendado)

Levanta toda la infraestructura (Frontend, Backend, Bases de Datos) en un solo paso:

```bash
docker-compose up --build
```
*   **Frontend**: http://localhost:80
*   **Backend Docs**: http://localhost:8000/docs
*   **Qdrant UI**: http://localhost:6333/dashboard

### Opción B: Ejecución Local (Desarrollo)

#### 1. Configuración del Backend

```bash
cd backend

# Crear archivo .env (ver sección de Configuración)
cp .env.example .env

# Instalar dependencias y ejecutar con uv (Recomendado)
uv sync
uv run uvicorn main:app --reload

# O con pip tradicional
# pip install -r requirements.txt
# uvicorn main:app --reload
```
La API estará disponible en `http://localhost:8000`.

#### 2. Configuración del Frontend

```bash
cd frontend/insurance-copilot

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```
El cliente web estará disponible en `http://localhost:4200`.

#### 3. Servicios Base (Bases de Datos)
Si ejecutas localmente, asegúrate de levantar al menos las bases de datos con Docker:
```bash
docker-compose up -d db qdrant
```

---

## ⚙️ Configuración (Variables de Entorno)

Crea un archivo `.env` en la carpeta `backend/` con las siguientes variables clave (basado en `backend/src/core/config.py`):

```env
# --- Base de Datos (PostgreSQL) ---
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=insurance_copilot

# --- Qdrant (Vector Database) ---
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY= # Opcional si usas local
QDRANT_COLLECTION_NAME=policies
QDRANT_SEMANTIC_COLLECTION_NAME=semantic_guardrails

# --- IA & RAG ---
OPENAI_API_KEY=sk-tu-api-key-aqui
LLM_MODEL=gpt-4o-mini
ENABLE_QUERY_EXPANSION=True
ENABLE_RERANKING=True
ENABLE_HYBRID_SEARCH=True

# --- Seguridad ---
SECRET_KEY=tu-clave-secreta-cambiala-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🧠 Ingesta de Datos (RAG)

Para que el asistente tenga conocimiento, debes procesar los documentos PDF:

1.  Coloca tus manuales/pólizas en `backend/data/`.
2.  Ejecuta el script de ingesta (híbrida):

```bash
cd backend
uv run python scripts/ingest.py
```
Este proceso vectorizará el contenido usando tanto embeddings densos como dispersos (SPLADE) y los indexará en Qdrant.

---

## 🧪 Endpoints Principales

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Registro de nuevos usuarios. |
| `POST` | `/api/v1/auth/token` | Login y obtención de JWT. |
| `POST` | `/api/v1/chat` | **Chatbot Inteligente**: Envía mensajes y recibe respuestas con contexto. |
| `POST` | `/api/v1/quotes/calculate`| Motor de cotización de seguros. |
