import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from qiskit_ibm_runtime import QiskitRuntimeService

#Se definen los cúbits que se van a necesitar para la posición, tanto en una dimensión como en otra, ya que darán los mismo pasos en las dos direcciones. 
#Estos se corresponden exactamente con el logaritmo en base dos de doble del número de pasos más uno, que se corresponde con la posición 0.
q_posicion_1D = 3
#Se calcula el número máximo de posiciones que se pueden escribir con el número de cúbits definido
num_max_pos = 2**q_posicion_1D
pasos = 2
#Se calcula el centro. Sin embargo, no será el centro exacto, debido a que siempre habrá posiciones potencia de 2,
#por lo que la posición centro no tendrá el mismo número de posiciones a cada lado.
centro = num_max_pos // 2 

#Se define el archivo que guardará los valores de las posiciones y sus probabilidades.
archivo = "hadamard_IBM_aachen_2.csv"
directorio = os.path.dirname(__file__)
ruta = os.path.join(directorio,archivo)


#Llamamos a IBM
service = QiskitRuntimeService()

#Decimos que trabajo debe leer
job_id = "d8q2d7qjm05s73fano8g"
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
    pos_prob = np.zeros((num_max_pos, num_max_pos))

    for bit_pos, n_veces in counts.items(): #Recorremos la lista, mirando cada bit y su probabilidad
        bit_sin_Control = bit_pos[:-2]
        pos_decimal_horizontal = int(bit_sin_Control[q_posicion_1D:], 2)
        pos_decimal_vertical = int(bit_sin_Control[:q_posicion_1D], 2)
        prob = n_veces/total_shots
        pos_prob [pos_decimal_horizontal, pos_decimal_vertical] += prob

    with open(ruta, mode = 'w', newline = '', encoding = 'utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Posición Horizontal', 'Posición Vertical', 'Probabilidad'])
        for (pos_decimal_horizontal, pos_decimal_vertical), prob in np.ndenumerate(pos_prob):
            writer.writerow([pos_decimal_horizontal - centro, pos_decimal_vertical - centro, prob])


    #Compruebo que las probabilidades suman 1
    #suma = np.sum(pos_prob)
    #print(suma)

    #Quito los impares, ya que su probabilidad es nula teóricamente
    #Seguramente en este caso no lo sea, pero para poder comparar las gráficas también se dejan fuera los impares
    Z_completa = pos_prob.reshape(num_max_pos,num_max_pos)

    posiciones = np.arange(num_max_pos) - centro

    quitarImpares = (posiciones % 2 == 0)
    posiciones_pares = posiciones[quitarImpares]
    Z_pares = Z_completa[quitarImpares, :][:, quitarImpares]

    indices_dentro = np.where((posiciones_pares >= -pasos) & (posiciones_pares <= pasos))[0]

    Z = Z_pares[np.ix_(indices_dentro, indices_dentro)]
    pos_final = posiciones_pares[indices_dentro]
    X, Y = np.meshgrid(pos_final, pos_final)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')


    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')

    #ax.set_title(f"Caminante 2D moneda Hadamard en {pasos} pasos")
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_zlabel('Probabilidad')

    #Para poder comparar las gráficas, se fija max_z como el valor máximo teórico
    #Para 2 pasos 0.25
    #Para 6 pasos 0.08
    #Para 10 pasos 0.07
    max_z = 0.25

    #Pongo el límite de cada eje
    ax.set_xlim(-(pasos), pasos)
    ax.set_ylim(-(pasos), pasos)
    ax.set_zlim(0, max_z * 1.1)

    ax.autoscale(False)

    norm = plt.Normalize(vmin=0, vmax=max_z)
    mapeo_color = plt.cm.ScalarMappable(norm=norm, cmap='viridis')
    fig.colorbar(mapeo_color, ax=ax, shrink=0.5, aspect=10, label='Probabilidad')

    plt.show()


    fig, ax = plt.subplots(figsize=(8, 7), layout="tight")

    im = ax.imshow(Z, cmap='viridis', origin='lower',
                vmin=0, vmax=max_z,
                extent=[pos_final[0], pos_final[-1], pos_final[0], pos_final[-1]])

    ax.set_xlabel('Posición en el Eje X')
    ax.set_ylabel('Posición en el Eje Y')

    marcas = np.arange(pos_final[0], pos_final[-1] + 1, 4)
    ax.set_xticks(marcas)
    ax.set_yticks(marcas)

    ax.set_aspect('equal')

    ax.grid(True, linestyle=":", alpha=0.3, color="white")

    cbar = fig.colorbar(im, ax=ax, shrink=0.8, aspect=15)
    cbar.set_label('Probabilidad', rotation=270, labelpad=15)

    plt.show()

else:
    print("El trabajo aún no ha terminado.")