import os

# Ruta base: carpeta donde está este script
ruta_base = os.path.dirname(os.path.abspath(__file__))

print(f"📂 Explorando el proyecto desde: {ruta_base}\n")

# Recorremos todo el árbol de carpetas
for carpeta_raiz, subcarpetas, archivos in os.walk(ruta_base):
    print(f"📁 Carpeta: {carpeta_raiz}")

    # Listar subcarpetas
    for sub in subcarpetas:
        print("   📂 Subcarpeta:", sub)

    # Listar archivos
    for archivo in archivos:
        print("   📄 Archivo:", archivo)

    print("-" * 40)
