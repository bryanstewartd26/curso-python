import os

# Mostrar la ruta actual donde está el script
ruta_actual = os.getcwd()
print("📂 Ruta actual:", ruta_actual)

# Listar los archivos y carpetas dentro de esa ruta
elementos = os.listdir(ruta_actual)
print("\n📋 Contenido de la carpeta actual:")
for e in elementos:
    print("-", e)