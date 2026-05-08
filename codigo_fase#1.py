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


def read_preview(path: Path, n: int = 5) -> pd.DataFrame:
    """Lee los encabezados y las primeras n filas del archivo."""
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path, nrows=n)
    return pd.read_csv(path, nrows=n)


def export_preview_csv(path: Path, output_path: Path, n: int = 5):
    """Exporta los encabezados y las primeras n filas a un CSV."""
    df = read_preview(path, n)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\nCSV exportado con encabezados y primeras {n} filas → {output_path.name}")


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
        # Exportar preview CSV
        output_csv = folder / "preview.csv"
        export_preview_csv(file_path, output_csv)
    except Exception as exc:
        print(f"Error al leer el encabezado de {file_path.name}: {exc}")


if __name__ == "__main__":
    main()