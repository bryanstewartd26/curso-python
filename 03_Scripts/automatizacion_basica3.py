import os

#Obtener direccion de ruta actual

print("Tu ruta actual es:")
print(os.getcwd())

#Mostras contenido dentro de la ruta actual

print("Contenido dentro de la ruta actual:")
print(os.listdir())
print("-" * 40)