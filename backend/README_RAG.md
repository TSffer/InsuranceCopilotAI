# 🧠 Advanced RAG Pipeline (Qdrant + Hybrid Search)

Este sistema utiliza una arquitectura de **Recuperación Aumentada (RAG)** de última generación para procesar pólizas de seguros y responder consultas legales con alta precisión.

## 🚀 Tecnologías Clave

- **Qdrant**: Base de datos vectorial de alto rendimiento.
- **Hybrid Search (Búsqueda Híbrida)**:
  - **Dense Vectors (Semántica)**: OpenAI `text-embedding-3-large`. Entiende el *significado*.
  - **Sparse Vectors (Keywords)**: `SPLADE` (vía `fastembed`). Entiende *términos exactos* y *jerga técnica*.
- **Query Expansion**: GPT-4o genera sinónimos para aumentar la cobertura de búsqueda.
- **Reranking**: `FlashRank` reordena los resultados para asegurar que lo más relevante esté al principio.

## 🛠️ Configuración e Ingesta

### 1. Iniciar Qdrant
Asegúrate de que el contenedor de Docker esté corriendo:
```bash
docker-compose up -d qdrant
```

### 2. Ejecutar Ingesta de Documentos
El script procesará todos los PDFs en la carpeta `backend/data`, generará los vectores híbridos e indexará todo en Qdrant.

```bash
cd backend
uv run python scripts/ingest.py
```

> **Nota**: La primera vez descargará el modelo SPLADE (aprox 500MB), por lo que puede tardar un poco.

## 🔍 Flujo de Consulta (RAG Pipeline)

1. **Usuario**: "¿Cubre robo de espejos?"
2. **Expansion**: Se generan variantes: "¿Cobertura de accesorios?", "¿Hurto parcial?".
3. **Retrieval (Qdrant)**:
    - Se busca por similitud semántica (Vectores Densos).
    - Se busca por palabras clave exactas (Vectores Dispersos).
    - Se combinan los resultados.
4. **Reranking (FlashRank)**: Se analizan los 20 mejores documentos y se reordenan por relevancia pura.
5. **Generación (GPT-4o)**: El LLM recibe los top-5 fragmentos y responde citando la fuente.

## ⚙️ Configuración (Variables de Entorno)

En `src/core/config.py` o `.env`:

- `ENABLE_HYBRID_SEARCH`: Activa/Desactiva vectores dispersos SPLADE.
- `ENABLE_RERANKING`: Activa/Desactiva FlashRank.
- `ENABLE_QUERY_EXPANSION`: Activa/Desactiva expansión de consultas.
