import asyncio
import os
import sys
from pypdf import PdfReader

# Add src to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.services.ingestion_service import IngestionService

# Ruta a la carpeta de datos
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))

async def process_pdf(file_path: str, ingestion_service: IngestionService, insurer_folder: str):
    filename = os.path.basename(file_path)
    print(f"Processing ({insurer_folder}): {filename}...")
    
    # Extracción de Texto
    try:
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    except Exception as e:
        print(f"Error reading PDF {filename}: {e}")
        return

    if not full_text.strip():
        print(f"Warning: No text extracted from {filename}")
        return
    
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
        # Fallback basado en nombres comunes
        if "riesgo" in filename.lower(): policy_type = "Todo Riesgo"
        elif "terceros" in filename.lower(): policy_type = "Resp. Civil / Terceros"
    
    # Construir metadatos
    metadata = {
        "source_file": filename,
        "insurer": insurer,
        "policy_type": policy_type,
        "year": year,
        "file_path": file_path
    }
    
    # Ingestar usando el servicio
    try:
        # Nota: process_document ya hace chunking y embedding
        chunks_indexed = await ingestion_service.process_document(full_text, metadata)
        print(f"Successfully indexed {chunks_indexed} chunks for {filename}")
    except Exception as e:
        print(f"Error indexing {filename}: {e}")

async def main():
    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} not found.")
        return

    print(f"Ingesting from: {DATA_DIR}")
    
    ingestion_service = IngestionService()
    
    # Recorrer subcarpetas (rimac, pacifico, etc)
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.lower().endswith(".pdf"):
                # El nombre de la carpeta padre es la aseguradora (ej: .../data/rimac -> rimac)
                insurer_folder = os.path.basename(root)
                # Si el archivo está en la raiz 'data', insurer_folder seria 'data'
                if insurer_folder == "data": 
                    insurer_folder = "Genérico"
                
                file_path = os.path.join(root, file)
                await process_pdf(file_path, ingestion_service, insurer_folder)

if __name__ == "__main__":
    asyncio.run(main())
