import cv2
from reconocimiento_facial import ReconocimientoFacial
from MySql import BaseDeDatos

def main():
    bd = BaseDeDatos()
    reconocimiento_facial = ReconocimientoFacial()

    while True:
        print("\n--- MENÚ ---")
        print("1. Registrar")
        print("2. Ingresar")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            # Registro de un nuevo usuario
            nombre, tipo_doc, num_doc, rostro = reconocimiento_facial.registrar_usuario()
            if rostro is not None:
                bd.guardar_usuario(nombre, tipo_doc, num_doc, rostro)
                print(f"Usuario {nombre} registrado correctamente.")
            else:
                print("No se pudo registrar el usuario.")

        elif opcion == "2":
            # Intento de ingreso
            nombre, num_doc = reconocimiento_facial.verificar_usuario(bd)
            if nombre:
                print(f"Bienvenido {nombre}, documento: {num_doc}")
            else:
                print("Usuario no válido.")

        elif opcion == "3":
            print("Saliendo...")
            break

        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()
