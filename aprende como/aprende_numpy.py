import numpy as np
#primeros pasos con numpy
lista1= [1, 2, 3] # lista de python, no es un array, es una lista de elementos
print("datos en lista")
print(lista1)
print(type(lista1))
#cambio a array de numpy
array1 = np.array(lista1)
print("datos en array")
print(array1)
print(type(array1))
#creacion de un array de dos dimensiones

array2 = np.array([[1, 2, 3], [4, 5, 6]])#esta compuesta por dos listas, cada una es una fila del array
print("array de dos dimensiones")
print(array2)

# matriz de ejemplo con índices
# [fila, columna]
matriz = np.array([[10, 20, 30],
                   [40, 50, 60],
                   [70, 80, 90]])
print("matriz con índices comentados")
print(matriz)
#forma (3,3) -> 3 filas y 3 columnas
#dimensión 2 -> es un array de dos dimensiones, porque tiene filas y columnas
# índices:
#     0, 1 ,  2
#0  [10, 20, 30]
#1  [40, 50, 60]
#2  [70, 80, 90]
# matriz[0,0] = 10, matriz[0,1] = 20, matriz[0,2] = 30
# matriz[1,0] = 40, matriz[1,1] = 50, matriz[1,2] = 60
# matriz[2,0] = 70, matriz[2,1] = 80, matriz[2,2] = 90

# Tipos de datos en NumPy
print("\n--- Tipos de datos ---")
# NumPy permite especificar el tipo de dato para optimizar memoria y rendimiento
array_int = np.array([1, 2, 3], dtype=np.int32)
array_float = np.array([1.0, 2.0, 3.0], dtype=np.float64)
array_bool = np.array([True, False, True], dtype=bool)
print("Array de enteros:", array_int, "dtype:", array_int.dtype)#Ccon el atributo dtype podemos ver el tipo de dato que tiene el array
print("Array de flotantes:", array_float, "dtype:", array_float.dtype)
print("Array booleano:", array_bool, "dtype:", array_bool.dtype)

# Operaciones aritméticas básicas
print("\n--- Operaciones aritméticas ---")
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print("a =", a)
print("b =", b)
print("a + b =", a + b)  # Suma elemento a elemento
print("a - b =", a - b)  # Resta
print("a * b =", a * b)  # Multiplicación elemento a elemento
print("a / b =", a / b)  # División
print("a ** 2 =", a ** 2)  # Potencia
    
# Funciones universales (ufuncs)
print("\n--- Funciones universales ---")
print("np.sqrt(a) =", np.sqrt(a))  # Raíz cuadrada
print("np.sin(a) =", np.sin(a))    # Seno
print("np.exp(a) =", np.exp(a))    # Exponencial
print("np.log(a) =", np.log(a))    # Logaritmo natural

# Indexación y slicing
print("\n--- Indexación y slicing ---")
arr = np.array([10, 20, 30, 40, 50])
print("arr =", arr)
print("arr[0] =", arr[0])        # Primer elemento
print("arr[-1] =", arr[-1])      # Último elemento
print("arr[1:4] =", arr[1:4])    # Del índice 1 al 3
print("arr[::2] =", arr[::2])    # Cada dos elementos

# Para arrays 2D
print("matriz[0, :] =", matriz[0, :])  # Primera fila
print("matriz[:, 1] =", matriz[:, 1])  # Segunda columna
print("matriz[1, :1] =", matriz[1, :1])  # Primera columna  y de laprimera fila a la segunda fila
print("matriz[1:3, 1:3] =", matriz[1:3, 1:3])  # Submatriz

# Manipulación de formas
print("\n--- Manipulación de formas ---")
arr_1d = np.array([1, 2, 3, 4, 5, 6])
print("arr_1d =", arr_1d)
arr_2d = arr_1d.reshape(2, 3)  # Cambiar forma a 2x3
print("arr_1d.reshape(2, 3) =", arr_2d)
print("arr_2d.flatten() =", arr_2d.flatten())  # Aplanar a 1D
print("arr_2d.T =", arr_2d.T)  # Transpuesta

# Broadcasting
print("\n--- Broadcasting ---")
# Operaciones entre arrays de diferentes formas
arr_small = np.array([1, 2, 3])
scalar = 10
print("arr_small =", arr_small)
print("scalar =", scalar)
print("arr_small + scalar =", arr_small + scalar)  # Broadcasting del escalar

arr_col = np.array([[1], [2], [3]])
arr_row = np.array([10, 20, 30])
print("arr_col =", arr_col)
print("arr_row =", arr_row)
print("arr_col + arr_row =", arr_col + arr_row)  # Broadcasting

# Estadísticas básicas
print("\n--- Estadísticas básicas ---")
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print("data =", data)
print("np.mean(data) =", np.mean(data))      # Media
print("np.median(data) =", np.median(data))  # Mediana
print("np.std(data) =", np.std(data))        # Desviación estándar
print("np.var(data) =", np.var(data))        # Varianza
print("np.min(data) =", np.min(data))        # Mínimo
print("np.max(data) =", np.max(data))        # Máximo
print("np.sum(data) =", np.sum(data))        # Suma total

# Arrays booleanos y máscaras
print("\n--- Arrays booleanos y máscaras ---")
numbers = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
mask = numbers > 5
print("numbers =", numbers)
print("mask (numbers > 5) =", mask)
print("numbers[mask] =", numbers[mask])  # Filtrar elementos

# Concatenación y stacking
print("\n--- Concatenación y stacking ---")
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])
print("arr1 =", arr1)
print("arr2 =", arr2)
print("np.concatenate([arr1, arr2]) =", np.concatenate([arr1, arr2]))  # Concatenar
print("np.vstack([arr1, arr2]) =", np.vstack([arr1, arr2]))  # Vertical stack
print("np.hstack([arr1, arr2]) =", np.hstack([arr1, arr2]))  # Horizontal stack

# Copias vs vistas
print("\n--- Copias vs vistas ---")
original = np.array([1, 2, 3, 4, 5])
vista = original[1:4]  # Vista (no copia los datos)
copia = original[1:4].copy()  # Copia profunda
print("original =", original)
print("vista =", vista)
print("copia =", copia)
vista[0] = 99  # Modifica el original
print("Después de modificar vista[0] = 99:")
print("original =", original)  # Cambió
print("vista =", vista)
print("copia =", copia)  # No cambió

# Generación de números aleatorios
print("\n--- Generación de números aleatorios ---")
np.random.seed(42)  # Para reproducibilidad
random_arr = np.random.rand(5,3)  # Array de 5 números aleatorios entre 0 y 1 con tamaño 5x3
random_int = np.random.randint(1, 10, 5)  # 5 enteros aleatorios entre 1 y 9 de tamaño 5
print("np.random.rand(5) =", random_arr)
print("np.random.randint(1, 10, 5) =", random_int)

# Guardar y cargar arrays / el cual es muy útil para guardar resultados intermedios o modelos entrenados
print("\n--- Guardar y cargar arrays ---")
# Guardar
np.save('mi_array', data)
print("Array guardado en 'mi_array.npy'")
# Cargar
loaded_array = np.load('mi_array')
print("Array cargado =", loaded_array)

# Arrays especiales
print("\n--- Arrays especiales ---")
zeros = np.zeros([2, 3])      # Array de ceros de tañmaño 2x3
ones = np.ones([2, 3])        # Array de unos de tamaño 2x3
identity = np.eye(3)          # Matriz identidad de tamaño 3x3
range_arr = np.arange(0, 10, 2)  # Array con rango de tamaño 2x3
linspace_arr = np.linspace(0, 1, 5)  # 5 puntos entre 0 y 1 
print("np.zeros((2, 3)) =", zeros)
print("np.ones((2, 3)) =", ones)
print("np.eye(3) =", identity)
print("np.arange(0, 10, 2) =", range_arr)
print("np.linspace(0, 1, 5) =", linspace_arr)

print("\n¡Fin del tutorial básico de NumPy!")
