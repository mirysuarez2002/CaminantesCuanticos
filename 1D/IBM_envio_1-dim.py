import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

#Se definen los cúbits que se van a necesitar para la posición. 
#Estos se corresponden exactamente con el logaritmo en base dos de doble del número de pasos más uno, que se corresponde con la posición 0.
q_posicion = 5
#Se calcula el número máximo de posiciones que se pueden escribir con el número de cúbits definido
num_max_pos = 2**q_posicion
pasos = 10
#Se calcula el centro. Sin embargo, no será el centro exacto, debido a que siempre habrá posiciones potencia de 2,
#por lo que la posición centro no tendrá el mismo número de posiciones a cada lado.
centro = num_max_pos // 2 

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

#Añadimos los operadores de medida
qc.measure_all()

#Llamamos a IBM
service = QiskitRuntimeService()
#Definimos el ordenador que queremos usar.
#NOTA: Para que esto funciona debe haberse conectado previamente con la API y la instancia correpondiente y 
#el ordenado que se quiera utilizar debe estar disponible para esa instancia
backend = service.backend("ibm_aachen")

#Transpilamos el circuito para ese ordenador
qc_transpilado = transpile(qc, backend=backend, optimization_level=3)
sampler = Sampler(mode = backend)

#Definimos el trabajo que vamos a mandar, con el número de ejecuciones (shots)
job = sampler.run([qc_transpilado], shots=10000)

#Escribimos por pantalla el código correspondiente al trabajo que hemos mandado
print(f"Job ID: {job.job_id()}")
