import os

ruta_base = "C:\\Users\\Monitoreo2\\Desktop\\Python_Lab"

for carpeta_raiz, subcarpetas, archivos in os.walk(ruta_base):
    for archivo in archivos:
        ruta_completa = os.path.join(carpeta_raiz, archivo)

        # Tamaño en bytes
        tamaño = os.path.getsize(ruta_completa)

        # Última fecha de modificación
        modificacion = os.path.getmtime(ruta_completa)

        print(f"📄 {archivo}")
        print(f"   📏 Tamaño: {tamaño} bytes")
        print(f"   ⏰ Modificado: {modificacion}")
        print("-" * 50)
