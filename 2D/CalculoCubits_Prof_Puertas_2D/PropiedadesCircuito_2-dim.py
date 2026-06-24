import numpy as np
import math
import matplotlib.pyplot as plt
import csv
import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService

#Se definen los archivos donde se guardaran los valores, que se crearan en la carpeta donde está el programa
archivo = "hadamard_puertas_prof.csv"
archivo_transpilado = "hadamard_puertas_prof_transpilado.csv"
directorio = os.path.dirname(__file__)
ruta = os.path.join(directorio,archivo)
ruta_transpilado = os.path.join(directorio,archivo_transpilado)

#Se llama a IBM para poder elegir con qué ordenador queremos construir el circuito transpilado
service = QiskitRuntimeService()
backend = service.backend("ibm_kingston")

#Se definen los pasos que se quieren usar y las listas vacias de profundidad y número 
#de cúbits y puertas para el circuito teórico y el transpilado
lista_pasos = [1,2,3,4,5,6,7,8,9,10]
lista_profundidad = []
lista_puertas = []
lista_qubits = []

lista_profundidad_transpilado = []
lista_puertas_transpilado = []
lista_qubits_transpilado = []

#Se define el circuito en función del número de pasos
def circuito(pasos):
    q_posicion_1D = math.ceil(math.log2(2*pasos+1))
    num_max_pos = 2**q_posicion_1D
    centro = num_max_pos // 2 

    #Se define el circuito cuántico con los cúbits de posición más un cúbit moneda
    qc = QuantumCircuit(q_posicion_1D + 1) 

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

    return qc


#Abrimos ambos archivos de texto
with open(ruta, mode = 'w', newline = '', encoding = 'utf-8') as f_estandar, open(ruta_transpilado, mode = 'w', newline = '', encoding = 'utf-8') as f_transpilado:
    writer_estandar = csv.writer(f_estandar)
    writer_transpilado = csv.writer(f_transpilado)


    writer_estandar.writerow(['Pasos', 'Qubits', 'Profundidad', 'Puertas Totales'])
    writer_transpilado.writerow(['Pasos', 'Qubits', 'Profundidad', 'Puertas Totales'])
    
    #Para cada valor de paso llamamos a la función circuito y calculamos sus propiedades usando las funciones de qiskit
    for p in lista_pasos:
        circ = circuito(p)
        qubits = circ.num_qubits
        profundidad = circ.depth()
        num_puertas = sum(circ.count_ops().values())

        lista_profundidad.append(profundidad)
        lista_puertas.append(num_puertas)
        lista_qubits.append(qubits)

        circ_t = transpile(circ, backend=backend)
        circ_t.remove_final_measurements() # Por si acaso hubiera medidores sueltos, ya que si los dejamos contarían como cúbits activos
        # Nos quedamos solo con los qubits activos (si no nos devuelve como valor el número total de cúbits del procesador)
        active_qubits = [q for gate in circ_t.data for q in gate.qubits]    
        qubits_t = len(set(active_qubits))
        profundidad_t = circ_t.depth()
        num_puertas_t = sum(circ_t.count_ops().values())

        lista_profundidad_transpilado.append(profundidad_t)
        lista_puertas_transpilado.append(num_puertas_t)
        lista_qubits_transpilado.append(qubits_t)


        #Se escriben todos los valores en los archivos
        writer_estandar.writerow([p, qubits, profundidad, num_puertas])
        writer_transpilado.writerow([p, qubits_t, profundidad_t, num_puertas_t])


#Se representan las figuras correspondientes

plt.figure(figsize=(7, 5))
plt.plot(lista_pasos, lista_qubits, color="black", linestyle="-", label="Teórico")
plt.plot(lista_pasos, lista_qubits_transpilado, color="#377eb8", linestyle="-", label="Transpilado (Kingston)")
plt.tick_params(labelsize=16)
plt.xlabel("Número de Pasos", fontsize=20)
plt.ylabel("Número de Cúbits", fontsize=20)
plt.xlim(0, 11)
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(fontsize=16)
plt.tight_layout()
plt.show()


plt.figure(figsize=(7, 5))
plt.plot(lista_pasos, lista_profundidad, color="black", linestyle="-", label="Teórico")
plt.plot(lista_pasos, lista_profundidad_transpilado, color="#377eb8", linestyle="-", label="Transpilado (Kingston)")
plt.xlabel("Número de Pasos", fontsize=20)
plt.ylabel("Profundidad", fontsize=20)
plt.tick_params(labelsize=16)
plt.xlim(0, 11)
plt.yscale("log")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(fontsize=16)
plt.tight_layout()
plt.show()


plt.figure(figsize=(7, 5))
plt.plot(lista_pasos, lista_puertas, color="black", linestyle="-", label="Teórico")
plt.plot(lista_pasos, lista_puertas_transpilado, color="#377eb8", linestyle="-", label="Transpilado (Kingston)")
plt.xlabel("Número de Pasos", fontsize=20)
plt.ylabel("Número de Puertas", fontsize=20)
plt.tick_params(labelsize=16)
plt.xlim(0, 11)
plt.yscale("log")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(fontsize=16)
plt.tight_layout()
plt.show()