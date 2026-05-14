import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import seaborn as sns

df_CalidadAire = pd.read_csv(r"C:\Users\samya\Desktop\codigos\Python\talento tech\Calidad_del_Aire_Antioquia.csv")
df_AguaEPM = pd.read_csv(r"C:\Users\samya\Desktop\codigos\Python\talento tech\Histórico_de_Tarifas_de_Acueducto_y_Aguas_Residuales_para_Hogares_–_EPM_20260430.csv")
df_RIPS = pd.read_csv(r"C:\Users\samya\Desktop\codigos\Python\talento tech\RIPS_Antioquia.csv")
def cambios_de_tipos_agua():
    # CAMBIO DE TIPOS DE VARIABLES EN EL df_AguaEPM: convertir columnas de dinero a valores numéricos
    currency_columns = [
        'Cargo Fijo',
        'Cargo por Consumo Menor',
        'Cargo por Consumo Mayor',
        'Cargo por Consumo',
        'Suspensión',
        'Reinstalación',
        'Reconexión',
        'Corte',
    ]
    def parse_currency(column):
        return (
            column
            .str.replace('$', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

    for col in currency_columns:
        df_AguaEPM[col] = parse_currency(df_AguaEPM[col])

    df_AguaEPM['Año'] = pd.to_datetime(df_AguaEPM['Año'], format='%Y').dt.year

def cambios_de_tipos_aire():
    print
    
cambios_de_tipos_agua()

print("todos los datos de df_AguaEPM ")
print(df_AguaEPM.head())
print(df_AguaEPM.info())


