# CaminantesCuanticos
Repositorio de los programas utilizados para la realización del Trabajo Fin de Máster: Simulación de caminantes aleatorios en ordenadores cuánticos para el Máster FisyMat de la UGR.

El trabajo consiste en la implementación de caminantes aleatorios cuánticos discretos en una y dos dimensiones. Dichos circuitos son analizados y, tras la comprobación de que funcionan correctamente, son ejecutados de cuatro formas:

    1. Vector teórico: Usa StateVector
    2. Simulación local sin ruido: Usa AerSimulator
    3. Simulación local con ruido: Usa AerSimulator con ruido.
    4. Hardware real: A través de la prataforma IBM Quantum Platform se hace uso de varios ordenadores cuánticos con procesador Heron.

Estas distintas ejecuciones son comparadas y se discuten los distintos resultados.


## Estructura del Repositorio
El repositorio se organiza en dos carpetas simétricas, una para una sola dimensión del caminante, '1D/', y otra para el caminante en dos dimensiones '2D/'. Fuera de estas dos carpetas se encuentra el archivo 'GuardaAPI.py', en la que se pueden rellenar los datos de la instancia propia y ejecutar el archivo para conectarse al servidor de IBM Quantum Platform. Esta parte será totalmente necesaria para ejecutar los archivos de las propiedades de los circuitos y los correspondientes a las ejecuciones tipo 3 y 4. Aún así, no todas las instancias tienen acceso a los cuatro ordenadores con procesador Heron utilizados en este trabajo. Por tanto, si algún archivo sigue sin funcionar tras conectarse a IBM consulte si el ordenador que aparece en el archivo está también disponible en su instancia.

* 'GuardarAPI.py':
* '1D/':
    * 5 programas .py para las ejecuciones (la ejecución en Hardware real tiene dos archivos, debido a que primero se envía el trabajo y luego se realiza la lectura)
    * 'CalculoCubits_Prof_Puertas': Contiene un archivo que calcula como crecen el número de cúbits, la profundidad y el número de puertas en función del paso.
    * 'CalculoCubits_Prof_Puertas': Contiene todos los archivos de datos '.csv' que se necesitan y los dos programas de cálculo de divergencia KL, uno de la distribución teórica con el hardware real ('KL_1-dim.py') y otro para la comparación de la distribución del simulador con ruido con hardware real ('KL_ruido_1-dim.py')
* '2D/':
    * 5 programas .py para las ejecuciones (la ejecución en Hardware real tiene dos archivos, debido a que primero se envía el trabajo y luego se realiza la lectura)
    * 'CalculoCubits_Prof_Puertas': Contiene un archivo que calcula como crecen el número de cúbits, la profundidad y el número de puertas en función del paso.
    * 'CalculoCubits_Prof_Puertas': Contiene todos los archivos de datos '.csv' que se necesitan y los dos programas de cálculo de divergencia KL, uno de la distribución teórica con el hardware real ('KL_2-dim.py') y otro para la comparación de la distribución del simulador con ruido con hardware real ('KL_ruido_2-dim.py')