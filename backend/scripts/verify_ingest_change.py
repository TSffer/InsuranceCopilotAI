
import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Add scripts dir to path to import ingest.py
sys.path.append(os.path.dirname(__file__))

# Mock IngestionService before importing ingest
sys.modules['src.services.ingestion_service'] = MagicMock()
from src.services.ingestion_service import IngestionService

# Now import ingest
import ingest

async def test_extraction():
    # Mock service
    mock_service = AsyncMock()
    mock_service.process_document.return_value = 5 # return 5 chunks

    # Sample file path
    filename = "Rimac_Vehicular_2026_Clausula Adicional_Auxilio Mecánico para Vehículos.pdf"
    file_path = os.path.join(os.path.dirname(__file__), "../data/rimac", filename)
    insurer_folder = "Rimac"

    # Run process_pdf
    # We need to mock PdfReader because the file might not exist or we don't want to read it
    with ingest.PdfReader as mock_pdf_reader: # Wait, ingest imports PdfReader class
        pass
    
    # Actually, ingest.py imports PdfReader. We need to mock it in ingest module.
    ingest.PdfReader = MagicMock()
    mock_pdf = MagicMock()
    mock_pdf.pages = []
    page = MagicMock()
    page.extract_text.return_value = "Sample text content."
    mock_pdf.pages = [page]
    ingest.PdfReader.return_value = mock_pdf

    print(f"Testing extraction for: {filename}")
    await ingest.process_pdf(file_path, mock_service, insurer_folder)

    # Verify calls
    if mock_service.process_document.called:
        args = mock_service.process_document.call_args
        content = args[0][0]
        metadata = args[0][1]
        
        print("\nExtracted Metadata:")
        for k, v in metadata.items():
            print(f"  {k}: {v}")

        # Assertions
        assert metadata['insurer'] == "Rimac"
        assert metadata['insurance_line'] == "Vehicular"
        assert metadata['year'] == "2026"
        assert metadata['document_type'] == "Clausula Adicional"
        assert metadata['description'] == "Auxilio Mecánico para Vehículos"
        print("\n✅ Verification Successful: Metadata matches expected values.")
    else:
        print("\n❌ Error: process_document was not called.")

if __name__ == "__main__":
    asyncio.run(test_extraction())
