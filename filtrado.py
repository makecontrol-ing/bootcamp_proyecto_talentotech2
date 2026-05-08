from pathlib import Path
import csv

input_csv = Path('Registros_Individuales_de_Prestación_de_Servicios_de_Salud_–_RIPS_20260502-002.csv')
output_dir = Path('base de datos filtrada')
output_dir.mkdir(parents=True, exist_ok=True)
output_csv = output_dir / 'Registros_Individuales_de_Prestación_de_Servicios_de_Salud_–_RIPS_20260502-002_Antioquia.csv'

with input_csv.open('r', encoding='utf-8', newline='') as f_in:
    reader = csv.DictReader(f_in)
    fieldnames = reader.fieldnames
    if fieldnames is None:
        raise ValueError('No se encontraron encabezados en el archivo CSV.')

    with output_csv.open('w', encoding='utf-8', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            if row.get('Departamento', '').strip() == '05 - Antioquia':
                writer.writerow(row)

print(f'Filtrado generado en: {output_csv}')