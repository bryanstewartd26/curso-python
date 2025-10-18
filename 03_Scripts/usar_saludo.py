#usar_saludo.py

# Importamos la funcion desde el otro archivo

import saludo_personalizado

# Usamos la funcion directamente, sin ejecutar el principal

mensaje = saludo_personalizado.crear_saludo("Bryan", 28)
print(mensaje)