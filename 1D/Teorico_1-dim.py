import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

#Se definen los cúbits que se van a necesitar para la posición. 
#Estos se corresponden exactamente con el logaritmo en base dos de doble del número de pasos más uno, que se corresponde con la posición 0.
q_posicion = 8
#Se calcula el número máximo de posiciones que se pueden escribir con el número de cúbits definido
num_max_pos = 2**q_posicion
pasos = 100
#Se calcula el centro. Sin embargo, no será el centro exacto, debido a que siempre habrá posiciones potencia de 2,
#por lo que la posición centro no tendrá el mismo número de posiciones a cada lado.
centro = num_max_pos // 2 
#Se define el archivo que guardará los valores de las posiciones y sus probabilidades.
archivo = "hadamard_teorico_100.csv"
directorio = os.path.dirname(__file__)
ruta = os.path.join(directorio,archivo)

#Se define el circuito cuántico con los cúbits de posición más un cúbit moneda
qc = QuantumCircuit(q_posicion + 1)

#Se necesita conocer el valor en binario del centro, para hacer más eficiente el programa
centro_binario = format(centro, f'0{q_posicion}b') #Se pasa el número a binario y se añaden los ceros que sean necesarios para completar la cadena de qubits
#Se coloca al caminante en el centro del sistema, variando los qubits necesarios de 0 a 1
#Se invierte la cadena de bit del centro, ya que qiskit los lee invertidos 
for i, bit in enumerate(reversed(centro_binario)):
    if bit == '1':
        qc.x(i + 1) #Se suma uno, debido al qubit de control
#Este proceso se podría usar para cualquier posición inicial, pero en los casos que se usan en este caso,
#donde se busca siempre que el caminante empiece en el centro, se podría añadir una sola puerta NOT al cúbit de más peso.

#Inicializamos el estado inicial en 1/raiz(2)(|arriba>+i|abajo>):
#Conseguimos el estado 1/raiz(2)(|arriba>+|abajo>)
qc.h(0)
#Tras esto, rotamos el estado con la matriz P, con theta=pi/2
qc.p(np.pi/2, 0)



for _ in range(pasos):
    #Aplicamos la moneda
    qc.h(0) 

    #Movemos a la derecha cuando sea necesario: Usamos una puerta multicontrolada para cada qubit
    for i in range(q_posicion, 0, -1):
        qc.mcx(list(range(i)), i)
    
    #Movemos a la izquierda cuando sea necesario: Usamos una puerta multicontrolada para cada qubit
    #Aplicamos las puertas X
    qc.x(0)
    for i in range(1, q_posicion):
        qc.x(i)


    #Movemos al caminante con puertas multicontroladas
    for i in range(q_posicion, 0, -1):
        qc.mcx(list(range(i)), i)
    

    #Volvemos a aplicar puertas X para volver a los valores reales
    for i in range(1, q_posicion):
        qc.x(i)
    qc.x(0) 

#Obtenemos las probabilidades con Statevector
estado = Statevector.from_instruction(qc) #Calcula la función de onda completa, sin medidas
probs = estado.probabilities_dict() #Escribe un listado con los bits y las probabilidades de cada uno

puertas_total = qc.count_ops()
print(puertas_total)

#Creamos el vector de probabilidades vacio
pos_prob = np.zeros(num_max_pos)


for bit_pos, prob_pos in probs.items(): #Recorremos la lista, mirando cada bit y su probabilidad
    pos_decimal = int(bit_pos[:-1], 2) #Se quita el último cúbit, que es el de la moneda, y se pasa de binario a decimal
    pos_prob[pos_decimal] += prob_pos


#Abrimos el archivo antes definido y copiamos los datos
with open(ruta, mode = 'w', newline = '', encoding = 'utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Posición', 'Probabilidad'])
    for pos, prob in enumerate(pos_prob):
        writer.writerow([pos - centro, prob])



#Compruebo que las probabilidades suman 1
#suma = np.sum(pos_prob)
#print(suma)

#Quito los impares, ya que su probabilidad es nula teóricamente
posiciones = np.arange(num_max_pos) - centro

quitarImpares = (posiciones%2 == 0)

posiciones_pares = posiciones[quitarImpares]
probabilidades_pares = pos_prob[quitarImpares]

#Pinto la gráfica correspondiente

plt.title(f"Caminante 1D Hadamard en {pasos} pasos")
plt.plot(posiciones_pares, probabilidades_pares)
plt.xlabel("Posición")
plt.ylabel("Probabilidad")

marcas_eje = np.arange(-(pasos+10), pasos+10, 4)
plt.xticks(marcas_eje)
plt.xlim(-(num_max_pos-centro),num_max_pos-centro)

plt.grid(True)

plt.show()