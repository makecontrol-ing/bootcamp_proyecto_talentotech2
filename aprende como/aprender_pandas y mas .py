import pandas as pan
import matplotlib.pyplot as plt #gráficas
# import seaborn as sns #gráficas más bonitas
import numpy as nppy

#dataframe
df = pan.DataFrame({    
    'col1': [1, 2, 3, 4, 5],
    'col2': [10, 20, 30, 40, 50],
    'col3': [100, 200, 300, 400, 500]
})
df.head() #muestra las primeras filas del dataframe, dentro del parentecis se puede indicar el número de filas a mostrar, por defecto es 5
df.head(2) #muestra las primeras 2 filas del dataframe

