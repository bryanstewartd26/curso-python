import os

ruta = "C:\\Users\\Monitoreo2\\Desktop\\Python_lab"
elementos = os.listdir(ruta)

print("Elementos dentro de la carpeta:")
for e in elementos:
    print(e)
