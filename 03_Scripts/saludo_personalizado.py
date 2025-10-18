#Saludo personalizado

#Creamos una funcion para saludar

def crear_saludo(nombre, edad):
    if edad > 30:
        return f"Hola {nombre}, tienes {edad} años. Aún estas en tu mejor momento"
    else:
        return f"Hola {nombre}, tienes {edad} años. Disfruta cada día!"
    
# Usamos el bloque principal para ejecutar el código

if __name__ == "__main__":

    #Pedimos los datos al usuario
    nombre = input("¿Cómo te llamas?:")

    try:
        edad = int(input("¿Cuántos años tienes?"))
        mensaje = crear_saludo(nombre, edad)
        print(mensaje)
    except ValueError:
        print("Por favor, ingrese un número válido para la edad")
