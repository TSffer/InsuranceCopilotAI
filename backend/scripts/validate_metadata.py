
import os
import sys

# Define path to data
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))

def extract_metadata(filename, folder_name):
    # Remove extension
    filename_clean = filename.replace(".pdf", "")
    parts = filename_clean.split("_")
    
    # Default values
    insurer = folder_name.capitalize()
    insurance_line = "Desconocido"
    year = "Desconocido"
    document_type = "Desconocido"
    description = "Desconocido"
    
    # Expected structure: INSURER_RAMO_YEAR_DOCTYPE_DESCRIPTION
    # Example: Rimac_Vehicular_2026_Clausula Adicional_Auxilio Mecánico para Vehículos.pdf
    
    if len(parts) >= 5:
        insurer = parts[0]
        insurance_line = parts[1]
        year = parts[2]
        document_type = parts[3]
        # Join the rest in case description has underscores (though it seems to use spaces)
        description = "_".join(parts[4:])
    elif len(parts) == 4:
         # Fallback for cases like Rimac_Vehicular_2026_CondicionesGenerales (if that exists)
         # or strictly 4 parts.
         insurer = parts[0]
         insurance_line = parts[1]
         year = parts[2]
         document_type = parts[3]
         description = "-"
    else:
        print(f"Warning: Filename {filename} does not match expected structure (>=5 parts)")
        
    return {
        "filename": filename,
        "insurer": insurer,
        "insurance_line": insurance_line,
        "year": year,
        "document_type": document_type,
        "description": description
    }

def main():
    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} not found.")
        return

    print(f"Scanning {DATA_DIR}...\n")
    
    processed_count = 0
    
    # Recorrer subcarpetas
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.lower().endswith(".pdf"):
                folder_name = os.path.basename(root)
                # Skip if root is data dir itself (though structure implies subfolders)
                if folder_name == "data":
                    folder_name = "Generico"
                
                metadata = extract_metadata(file, folder_name)
                
                print(f"File: {file}")
                print(f"  Insurer: {metadata['insurer']}")
                print(f"  Line: {metadata['insurance_line']}")
                print(f"  Year: {metadata['year']}")
                print(f"  Type: {metadata['document_type']}")
                print(f"  Desc: {metadata['description']}")
                print("-" * 40)
                
                processed_count += 1
                
    print(f"\nTotal files checked: {processed_count}")

if __name__ == "__main__":
    main()
