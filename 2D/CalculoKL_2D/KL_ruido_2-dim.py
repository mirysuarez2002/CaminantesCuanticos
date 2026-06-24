import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import rel_entr
import numpy as np
import os

#Se define la dirección de todos los archivos como la carpeta en la que se encuentra el programa
directorio = os.path.dirname(__file__)

#Se definen los nombres de los archivos, separando por ordenadores
archivos1 = [("hadamard_simOrdenador_Ruido_fez_2.csv", "hadamard_IBM_fez_2.csv", 2),
            ("hadamard_simOrdenador_Ruido_fez_6.csv", "hadamard_IBM_fez_6.csv", 6),
            ("hadamard_simOrdenador_Ruido_fez_10.csv", "hadamard_IBM_fez_10.csv",10)]

archivos2 = [("hadamard_simOrdenador_Ruido_kingston_2.csv", "hadamard_IBM_kingston_2.csv", 2),
            ("hadamard_simOrdenador_Ruido_kingston_6.csv", "hadamard_IBM_kingston_6.csv", 6),
            ("hadamard_simOrdenador_Ruido_kingston_10.csv", "hadamard_IBM_kingston_10.csv",10)]

archivos3 = [("hadamard_simOrdenador_Ruido_marrakesh_2.csv", "hadamard_IBM_marrakesh_2.csv", 2),
            ("hadamard_simOrdenador_Ruido_marrakesh_6.csv", "hadamard_IBM_marrakesh_6.csv", 6),
            ("hadamard_simOrdenador_Ruido_marrakesh_10.csv", "hadamard_IBM_marrakesh_10.csv",10)]

archivos4 = [("hadamard_simOrdenador_Ruido_aachen_2.csv", "hadamard_IBM_aachen_2.csv", 2),
            ("hadamard_simOrdenador_Ruido_aachen_6.csv", "hadamard_IBM_aachen_6.csv", 6),
            ("hadamard_simOrdenador_Ruido_aachen_10.csv", "hadamard_IBM_aachen_10.csv",10)]

#Se definen los pasos que se han utilizado y las listas en blanco para guardar los valores de la divergencia
lista_pasos = [2,6,10]
lista_divergencia_1 = []
lista_divergencia_2 = []
lista_divergencia_3 = []
lista_divergencia_4 = []

#Definimos la función divergencia para calcular el valor de KL
def divergencia(df_teo, df_real):
    # Extraemos la segunda columna de cada archivo (usando el índice 2)
    col_teo = df_teo.iloc[:, 2]
    col_real = df_real.iloc[:, 2]

    #Se sustituyen los valores nulos por 1*10^(-9), para evitar dividir entre 0
    col_teo = col_teo.replace(0, 1e-9)
    col_real = col_real.replace(0, 1e-9)
    
    #Se realiza el calculo de KL, para pasar a logaritmo en base 2 se divide entre el logartimo de 2
    KL = np.sum(rel_entr(col_teo, col_real)) / np.log(2)
    
    #Se devuelve el valor de la divergencia
    return KL


#Se van calculando los valores de KL con la función para cada ordenador y 
#cada número de pasos y se escribe por pantalla
print("Ordenador IBM Fez")

for f_teo, f_sim, n_pasos in archivos1: 
    ruta_teo = os.path.join(directorio, f_teo)
    ruta_sim = os.path.join(directorio, f_sim)

    df_teo = pd.read_csv(ruta_teo)
    df_sim = pd.read_csv(ruta_sim)

    resultado = divergencia(df_teo,df_sim)

    lista_divergencia_1.append(resultado)

    print(f"Pasos {n_pasos}: Divergencia = {resultado:.6f}")


print("Ordenador IBM Kingston")

for f_teo, f_sim, n_pasos in archivos2: 
    ruta_teo = os.path.join(directorio, f_teo)
    ruta_sim = os.path.join(directorio, f_sim)

    df_teo = pd.read_csv(ruta_teo)
    df_sim = pd.read_csv(ruta_sim)

    resultado = divergencia(df_teo,df_sim)

    lista_divergencia_2.append(resultado)

    print(f"Pasos {n_pasos}: Divergencia = {resultado:.6f}")


print("Ordenador IBM Marrakesh")

for f_teo, f_sim, n_pasos in archivos3: 
    ruta_teo = os.path.join(directorio, f_teo)
    ruta_sim = os.path.join(directorio, f_sim)

    df_teo = pd.read_csv(ruta_teo)
    df_sim = pd.read_csv(ruta_sim)

    resultado = divergencia(df_teo,df_sim)

    lista_divergencia_3.append(resultado)

    print(f"Pasos {n_pasos}: Divergencia = {resultado:.6f}")

print("Ordenador IBM Aachen")

for f_teo, f_sim, n_pasos in archivos4: 
    ruta_teo = os.path.join(directorio, f_teo)
    ruta_sim = os.path.join(directorio, f_sim)

    df_teo = pd.read_csv(ruta_teo)
    df_sim = pd.read_csv(ruta_sim)

    resultado = divergencia(df_teo,df_sim)

    lista_divergencia_4.append(resultado)

    print(f"Pasos {n_pasos}: Divergencia = {resultado:.6f}")

#Por último se realiza la gráfica

plt.figure(figsize=(8, 5))
plt.plot(lista_pasos, lista_divergencia_1, marker='o', linestyle='-', label='ibm_fez', color='#e41a1c')
plt.plot(lista_pasos, lista_divergencia_2, marker='s', linestyle='-', label='ibm_kingston', color='#377eb8')
plt.plot(lista_pasos, lista_divergencia_3, marker='^', linestyle='-', label='ibm_marrakesh', color='#4daf4a')
plt.plot(lista_pasos, lista_divergencia_4, marker='P', linestyle='-', label='ibm_aachen', color='#984ea3')

plt.title('Simulación con Ruido vs Ordenador Cuántico IBM')
plt.xlabel('Número de Pasos', fontsize=15)
plt.ylabel('Divergencia', fontsize=15)

plt.tick_params(labelsize=13)
plt.xlim(1,11)
plt.ylim(-0.05,8.5)

plt.grid(True)

plt.legend(fontsize=13)

plt.show()