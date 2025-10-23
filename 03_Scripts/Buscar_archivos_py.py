import os

ruta_base = "C:\\Users\\Monitoreo2\\Desktop\\Python_lab"

print("Buscando archivos .py en todo el proyecto...\n")

for carpeta_raiz, subcarpetas, archivos in os.walk(ruta_base):
    for archivos in archivos:
        if archivos.endswith(".py"):
            ruta_completa = os.path.join(carpeta_raiz, archivos)
            print(ruta_completa)
