from Funciones import ConexionBD, login, mostrar_menu, listarEstudiantes, agregarEstudiante, borrarEstudiante, buscarEstudiante, modificarEstudiante, listarProfesoresYCursos, borrarProfesor, agregarEstudianteACurso, crearCurso, crearProfesor, listarCursosDetalle, listarEstudiantesPorCurso
import os
from dotenv import load_dotenv
load_dotenv()



def main():
    db = ConexionBD()
    db.conectar()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        clear = lambda: os.system('cls')
        clear()
        #LISTAR ESTUDIANTE
        if opcion == "1":
            listarEstudiantes(db)

        #AGREGAR ESTUDIANTE
        elif opcion == "2":
            agregarEstudiante(db)

        #Buscar Estudiante
        elif opcion == "3":
            buscarEstudiante(db)

        #Eliminar Estudiante
        elif opcion == "4":
            borrarEstudiante(db)

        #MODIFICAR ESTUDIANTE POR ID
        elif opcion == "5":
            modificarEstudiante(db)

        #Profesores
        elif opcion == "6":
            listarProfesoresYCursos(db)

         #ELIMINAR PROFESOR POR ID
        elif opcion == "7":
            borrarProfesor(db)

        #Agregar estudiante a curso
        elif opcion == "8":
            agregarEstudianteACurso(db)
        
        # CREAR CURSO
        elif opcion == "9":
            crearCurso(db)

        # CREAR PROFESOR 
        elif opcion == "10":
            crearProfesor(db)
        # LISTAR CURSOS (DETALLE) 
        elif opcion == "11":
            listarCursosDetalle(db)

        # LISTAR ESTUDIANTES POR CURSO
        elif opcion == "12":
            listarEstudiantesPorCurso(db)
        # SALIR       
        elif opcion == "13":
            print("\nSaliendo")
            db.cerrar_conexion()
            break
        else:
            clear = lambda: os.system('cls')
            clear()
            print("\033[31mOpción inválida. Intente de nuevo.\033[0m")
            continue

if __name__ == "__main__":
    if login():
        main()
