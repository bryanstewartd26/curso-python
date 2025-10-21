import os

#Obtener direccion de ruta actual

print("Tu ruta actual es:")
print(os.getcwd())

#Mostras contenido dentro de la ruta actual

print("Contenido dentro de la ruta actual:")
print(os.listdir())
print("-" * 40)

#Creamos una carpeta nueva

nueva_carpeta = "carpeta prueba"
#os.mkdir(nueva_carpeta) comentamos porque no podemos crear una carpeta que ya existe
print(f"Carpeta '{nueva_carpeta}' creada correctamente")
print(os.listdir()) #Verificamos que ahora aparece en la lista
print("-" * 40)

#Creamos un archivo dentro de la carpeta nueva

os.chdir(nueva_carpeta)

print("Directorio Nuevo de Trabajo:")
print(os.getcwd())
print("-" * 40)

#Creamos un archivo dentro de la carpeta nuevo

#with open("archivo.txt", "w") as archivo:
    #archivo.write("Hola Bryan, esto fue creado desde Python")
print("Archivo creado dentro de la carpeta prueba")
print("-" * 40)

#Volvemos a la carpeta anterior
os.chdir("..")
print("Volvimos a la carpeta anterior")
print(os.getcwd())
print("-" * 40)

# Eliminamos la carpeta creada (Solo si esta vacia)

os.remove("carpeta prueba/archivo.txt") #eliminamos el archivo primero
os.rmdir("carpeta prueba") #Luego la carpeta vacía
print("Carpeta y archivo correctamente.")
print("-" * 40)