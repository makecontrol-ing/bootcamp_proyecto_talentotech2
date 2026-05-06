from pathlib import Path
import pandas as pd


def find_data_file(folder: Path):
    patterns = ["*.xlsx", "*.xls", "*.csv"]
    for pattern in patterns:
        for path in sorted(folder.glob(pattern)):
            return path
    return None


def read_header(path: Path):
    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path, nrows=0)
    else:
        df = pd.read_csv(path, nrows=0)
    return list(df.columns), df.shape


def main():
    folder = Path(__file__).resolve().parent
    file_path = find_data_file(folder)

    if file_path is None:
        print("No se encontró ningún archivo Excel o CSV en la carpeta.")
        return

    print(f"Archivo detectado: {file_path.name}")
    try:
        header, shape = read_header(file_path)
        print(f"Shape: {shape}")
        print("Encabezado:")
        for i, column in enumerate(header, start=1):
            print(f"{i}. {column}")
    except Exception as exc:
        print(f"Error al leer el encabezado de {file_path.name}: {exc}")


if __name__ == "__main__":
    main()
