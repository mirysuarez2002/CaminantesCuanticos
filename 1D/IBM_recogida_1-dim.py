import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from qiskit_ibm_runtime import QiskitRuntimeService

#Se definen los cúbits que se van a necesitar para la posición. 
#Estos se corresponden exactamente con el logaritmo en base dos de doble del número de pasos más uno, que se corresponde con la posición 0.
q_posicion = 5
#Se calcula el número máximo de posiciones que se pueden escribir con el número de cúbits definido
num_max_pos = 2**q_posicion
pasos = 10
#Se calcula el centro. Sin embargo, no será el centro exacto, debido a que siempre habrá posiciones potencia de 2,
#por lo que la posición centro no tendrá el mismo número de posiciones a cada lado.
centro = num_max_pos // 2 

#Se define el archivo que guardará los valores de las posiciones y sus probabilidades.
archivo = "hadamard_IBM_aachen_10.csv"
directorio = os.path.dirname(__file__)
ruta = os.path.join(directorio,archivo)

#Llamamos a IBM
service = QiskitRuntimeService()

#Decimos que trabajo debe leer
job_id = "d809di11mjqc73ajnktg"
job = service.job(job_id)

#Nos dice si sigue en cola, se está ejecutando o ya está terminado
print(f"Estado del trabajo: {job.status()}")

#Si está terminado recoge los datos igual 
#que el resto de archivos y pinta la gráfica correspondiente y copia los datos en el archivo.
#Si aún no ha terminado lo dice por pantalla
if job.status() == 'DONE':
    result = job.result()
    pub_result = result[0]
    counts=result[0].data.meas.get_counts()

    total_shots = sum(counts.values()) #Número total de shots

    #Creamos el vector de probabilidades vacio
    pos_prob = np.zeros((num_max_pos))

    for bit_pos, n_veces in counts.items(): #Recorremos la lista, mirando cada bit y su probabilidad
        pos_decimal = int(bit_pos[:-1], 2) 
        prob = n_veces/total_shots
        pos_prob[pos_decimal] += prob


    with open(ruta, mode = 'w', newline = '', encoding = 'utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Posición', 'Probabilidad'])
        for pos, prob in enumerate(pos_prob):
            writer.writerow([pos - centro, prob])


    #Compruebo que las probabilidades suman 1
    #suma = np.sum(pos_prob)
    #print(suma)

    #Quito los impares, ya que su probabilidad es nula
    posiciones = np.arange(num_max_pos) - centro

    quitarImpares = (posiciones%2 == 0)

    posiciones_pares = posiciones[quitarImpares]
    probabilidades_pares = pos_prob[quitarImpares]

    plt.title(f"Caminante 1D Hadamard en {pasos} pasos ejecución ordenador ibm_aachen")
    plt.plot(posiciones_pares, probabilidades_pares)
    plt.xlabel("Posición")
    plt.ylabel("Probabilidad")

    marcas_eje = np.arange(-(pasos+10), pasos+10, 4)
    plt.xticks(marcas_eje)
    plt.xlim(-(num_max_pos-centro),num_max_pos-centro)

    plt.grid(True)

    plt.show()

else:
    print("El trabajo aún no ha terminado.")