from qiskit_ibm_runtime import QiskitRuntimeService

token = ""      # Añade un API Token
instance = ""   # Pegar el CRN
region = "" #Indicar región

# Guardar la cuenta
service = QiskitRuntimeService.save_account(
    token=token,
    instance=instance,
    overwrite=True
    )

# Verificación de que está guardada
print("Verificando conexión con IBM Quantum...")
try:
    service = QiskitRuntimeService(channel="ibm_cloud")
    print("Conexión establecida con éxito.")
except Exception as e:
    print(f"Error de autenticación. Detalles: {e}")