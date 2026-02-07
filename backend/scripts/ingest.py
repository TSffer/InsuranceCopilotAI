import asyncio
import os
import sys
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.database import AsyncSessionLocal
from src.domain.models import Policy
from src.core.config import settings

# Ruta a la carpeta de datos
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))

async def get_embedding(client: AsyncOpenAI, text: str):
    response = await client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

async def process_pdf(file_path: str, client: AsyncOpenAI, db: AsyncSession, insurer_folder: str):
    filename = os.path.basename(file_path)
    print(f"Processing ({insurer_folder}): {filename}...")
    
    # Extracción de Texto
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    
    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_text(full_text)
    
    # Inferir metadatos del nombre de archivo: [ASEGURADORA]_[TIPO_PLAN]_[AÑO].pdf
    filename_clean = filename.replace(".pdf", "")
    parts = filename_clean.split("_")
    
    insurer = insurer_folder.capitalize()
    policy_type = "Generico"
    year = "2024"
    
    if len(parts) >= 2:
        # Si tiene 2 partes: Rimac_TodoRiesgo
        insurer = parts[0]
        policy_type = parts[1].replace("-", " ")
        if len(parts) >= 3:
            # Si tiene 3 partes: Rimac_TodoRiesgo_2024
            year = parts[2]
    else:
        # Fallback
        if "riesgo" in filename.lower(): policy_type = "Todo Riesgo"
        elif "terceros" in filename.lower(): policy_type = "Resp. Civil / Terceros"
    
    tasks = []
    
    # Procesar chunks 
    for i, chunk in enumerate(chunks):
        # Augmentación de Texto
        augmented_text = f"Aseguradora: {insurer}. Plan: {policy_type}. Año: {year}. Documento: {filename}. Contenido: {chunk}"
        
        # Obtenemos vector del texto aumentado
        embedding = await get_embedding(client, augmented_text)
        
        policy = Policy(
            insurer_name=insurer,
            policy_type=policy_type,
            base_price=500.0, 
            content_text=chunk,
            embedding=embedding,
            metadata_json={"source": filename, "year": year, "chunk_index": i, "total_chunks": len(chunks)}
        )
        db.add(policy)
        
        # Guardar cada 50 chunks
        if i % 50 == 0:
            await db.commit()
    
    await db.commit()
    print(f"Saved {len(chunks)} chunks for {filename}")

async def main():
    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} not found.")
        return

    print(f"Ingesting from: {DATA_DIR}")
    
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async with AsyncSessionLocal() as db:
        # Recorrer subcarpetas (rimac, pacifico, etc)
        for root, dirs, files in os.walk(DATA_DIR):
            for file in files:
                if file.lower().endswith(".pdf"):
                    # El nombre de la carpeta padre es la aseguradora (ej: .../data/rimac -> rimac)
                    insurer_folder = os.path.basename(root)
                    if insurer_folder == "data": insurer_folder = "Unknown"
                    
                    file_path = os.path.join(root, file)
                    try:
                        await process_pdf(file_path, client, db, insurer_folder)
                    except Exception as e:
                        print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
