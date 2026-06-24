import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

#Se definen los cúbits que se van a necesitar para la posición, tanto en una dimensión como en otra, ya que darán los mismo pasos en las dos direcciones. 
#Estos se corresponden exactamente con el logaritmo en base dos de doble del número de pasos más uno, que se corresponde con la posición 0.
q_posicion_1D = 3
#Se calcula el número máximo de posiciones que se pueden escribir con el número de cúbits definido
num_max_pos = 2**q_posicion_1D
pasos = 2
#Se calcula el centro. Sin embargo, no será el centro exacto, debido a que siempre habrá posiciones potencia de 2,
#por lo que la posición centro no tendrá el mismo número de posiciones a cada lado.
centro = num_max_pos // 2 

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

#Llamamos a IBM
service = QiskitRuntimeService()
#Definimos el ordenador que queremos usar.
#NOTA: Para que esto funciona debe haberse conectado previamente con la API y la instancia correpondiente y 
#el ordenado que se quiera utilizar debe estar disponible para esa instancia
backend = service.backend("ibm_aachen")

#Transpilamos el circuito para ese ordenador
qc_transpilado = transpile(qc, backend=backend)
sampler = Sampler(mode = backend)

#Definimos el trabajo que vamos a mandar, con el número de ejecuciones (shots)
job = sampler.run([qc_transpilado], shots=10000)

#Escribimos por pantalla el código correspondiente al trabajo que hemos mandado
print(f"Job ID: {job.job_id()}")
