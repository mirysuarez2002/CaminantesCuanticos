import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

#Se definen los cúbits que se van a necesitar para la posición, tanto en una dimensión como en otra, ya que darán los mismo pasos en las dos direcciones. 
#Estos se corresponden exactamente con el logaritmo en base dos de doble del número de pasos más uno, que se corresponde con la posición 0.
q_posicion_1D = 5
#Se calcula el número máximo de posiciones que se pueden escribir con el número de cúbits definido
num_max_pos = 2**q_posicion_1D
pasos = 10
#Se calcula el centro. Sin embargo, no será el centro exacto, debido a que siempre habrá posiciones potencia de 2,
#por lo que la posición centro no tendrá el mismo número de posiciones a cada lado.
centro = num_max_pos // 2 
#Se define el archivo que guardará los valores de las posiciones y sus probabilidades.
archivo = "hadamard_simOrdenador_10.csv"
directorio = os.path.dirname(__file__)
ruta = os.path.join(directorio,archivo)

#Se define el circuito cuántico con los cúbits de posición de ambas dimensiones más dos cúbits moneda, uno por dimensión
qc = QuantumCircuit(q_posicion_1D*2 + 2) #Añadimos los qubits de la moneda

#Se necesita conocer el valor en binario del centro, para hacer más eficiente el programa
centro_binario = format(centro, f'0{q_posicion_1D}b') #Se pasa el número a binario y se añaden los ceros que sean necesarios para completar la cadena de qubits
#Se coloca al caminante en el centro del sistema, variando los qubits necesarios de 0 a 1
#Se invierte la cadena de bit del centro, ya que qiskit los lee invertidos 
#Se pone en la posición centro en ambas direcciones
for i, bit in enumerate(reversed(centro_binario)):
    if bit == '1':
        qc.x(i + 2) #Se suma dos, debido a los qubits de control
        qc.x(i + 2 + q_posicion_1D) #Se suma los dos qubits de control y los 6 qubits de la dirección horizontal, para inicializar también la vertical en 0
#Este proceso se podría usar para cualquier posición inicial, pero en los casos que se usan en este caso,
#donde se busca siempre que el caminante empiece en el centro, se podría añadir una sola puerta NOT al cúbit de más peso para ambas dimension.


#Inicializamos el estado inicial:
#Conseguimos el estado 1/raiz(2)(|izq>+|der>)
qc.h(0)

#Conseguimos el estado 1/raiz(2)(|abajo>+|arriba>)
qc.h(1)

#Tras esto, rotamos el estado con la matriz P, con theta=pi/2 en ambos qubits de control
qc.p(np.pi/2, 0)
qc.p(np.pi/2, 1)




for _ in range(pasos):
    #Aplicamos la moneda
    qc.h(0) 
    qc.h(1)

    #Movemos a la derecha cuando sea necesario: Usamos una puerta multicontrolada para cada qubit 
    for i in range(q_posicion_1D+1, 1, -1):
        controles = [0] + list(range(2, i))
        qc.mcx(controles, i)

    #Movemos hacia arriba cuando sea necesario: Usamos una puerta multicontrolada para cada qubit 
    for i in range(q_posicion_1D*2+1, q_posicion_1D+1, -1):
        controles = [1] + list(range(q_posicion_1D+2, i))
        qc.mcx(controles, i)


    
    #Movemos a la izquierda y hacia abajo cuando sea necesario: Usamos una puerta multicontrolada para cada qubit
    #Aplicamos las puertas X
    qc.x(0)
    qc.x(1)
    for i in range(2, q_posicion_1D*2+2):
        qc.x(i)


    for i in range(q_posicion_1D+1, 1, -1):
        controles = [0] + list(range(2, i))
        qc.mcx(controles, i)

    for i in range(q_posicion_1D*2+1, q_posicion_1D+1, -1):
        controles = [1] + list(range(q_posicion_1D+2, i))
        qc.mcx(controles, i)
    

    #Aplicamos las puertas X
    qc.x(0)
    qc.x(1)
    for i in range(2, q_posicion_1D*2+2):
        qc.x(i)


#Añadimos los operadores de medida
qc.measure_all()

#Llamamos al simulador
sim=AerSimulator()
#Definimos el resultado con el simulador e indicando el número de veces que queremos que se ejecute (shots)
result=sim.run(qc, shots=10000).result()

#Obtenemos cada resultado
counts=result.get_counts()

#Sumamos cuantos valores hemos obtenido: Número total de shots
total_shots = sum(counts.values()) #Número total de shots

#Creamos el vector de probabilidades vacio
pos_prob = np.zeros((num_max_pos, num_max_pos))

for bit_pos, n_veces in counts.items(): #Recorremos la lista, mirando cada bit y su probabilidad
    bit_sin_Control = bit_pos[:-2] #Se quitan los últimos dos cúbits, que son los cúbits moneda
    pos_decimal_horizontal = int(bit_sin_Control[q_posicion_1D:], 2) #Me quedo con la segunda mitad del string de cúbits de posiciones y pasamos a binario, que corresponde con la posición horizontal
    pos_decimal_vertical = int(bit_sin_Control[:q_posicion_1D], 2) #Hago lo mismo con la primera mitad. Es la posición vertical.
    prob = n_veces/total_shots #Calculamos la probabilidad dividiendo las veces que ha terminado en esa posición entre el número de shots
    pos_prob [pos_decimal_horizontal, pos_decimal_vertical] += prob #Sumamos todas las probabilidades de la posición, ignorando el estado moneda

#Abrimos el archivo antes definido y copiamos los datos
with open(ruta, mode = 'w', newline = '', encoding = 'utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Posición Horizontal', 'Posición Vertical', 'Probabilidad'])
    for (pos_decimal_horizontal, pos_decimal_vertical), prob in np.ndenumerate(pos_prob):
        writer.writerow([pos_decimal_horizontal - centro, pos_decimal_vertical - centro, prob])



#Compruebo que las probabilidades suman 1
#suma = np.sum(pos_prob)
#print(suma)

#Quito los impares, ya que su probabilidad es nula teóricamente
Z_completa = pos_prob.reshape(num_max_pos,num_max_pos)

posiciones = np.arange(num_max_pos) - centro

quitarImpares = (posiciones % 2 == 0)
posiciones_pares = posiciones[quitarImpares]
Z_pares = Z_completa[quitarImpares, :][:, quitarImpares]

#Elimino los valores de probabilidad para posiciones mayores, en valor absoluto, al número de pasos, para que se vea mejor la gráfica 3D
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

#Fijo el valor máximo en un punto un poco superior al máximo real (No dejo el valor real para usar exactamente el mismo en el resto de gráficas)
#Para 2 pasos 0.25
#Para 6 pasos 0.08
#Para 10 pasos 0.07
max_z = 0.07

#Pongo el límite de cada eje
ax.set_xlim(-(pasos), pasos)
ax.set_ylim(-(pasos), pasos)
ax.set_zlim(0, max_z * 1.1)

ax.autoscale(False)

norm = plt.Normalize(vmin=0, vmax=max_z)
mapeo_color = plt.cm.ScalarMappable(norm=norm, cmap='viridis')
fig.colorbar(mapeo_color, ax=ax, shrink=0.5, aspect=10, label='Probabilidad')

plt.show()


#Otra gráfica, para que se vea mejor
#Creamos la proyección en 2D de las probabilidades
fig, ax = plt.subplots(figsize=(8, 7), layout="tight")

# Pintamos la matriz con imshow
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