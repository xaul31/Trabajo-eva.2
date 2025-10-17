from Funciones import ConexionBD, login, mostrar_menu, listarEstudiantes, agregarEstudiante, borrarEstudiante, buscarEstudiante, modificarEstudiante
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
            try:
                print("\n--- Lista de Profesores y sus Cursos ---")
                profesores = db.ejecutar_consulta("SELECT id, nombre FROM profesores")
                cursos = db.ejecutar_consulta("SELECT id, nombre, profesor_id FROM cursos")
                for prof in profesores:
                    cursos_prof = [c[1] for c in cursos if c[2] == prof[0]]
                    if cursos_prof:
                        for curso in cursos_prof:
                            print(f"Profesor id: {prof[0]}, Nombre: \033[92m{prof[1]}\033[0m, Curso: {curso}")
                    else:
                        print(f"Profesor id: {prof[0]}, Nombre: \033[92m{prof[1]}\033[0m, Curso: Sin curso asignado")
                print("-"*34)
            except Exception as e:
                print("Error al recuperar la lista de profesores:", e)
         #ELIMINAR PROFESOR POR ID
        elif opcion == "7":
            try:
                print("\n--- Lista de Profesores ---")
                profesores = db.ejecutar_consulta("Select * from profesores")
                for prof in profesores:
                    print(f"id: {prof[0]}, Nombre: \033[92m{prof[1]}\033[0m")
                print("-"*34)
                profesor_a_eliminar = int(input("Ingrese el ID del profesor a eliminar: "))
                # Verificar si el profesor tiene cursos asignados
                cursos_profesor = db.ejecutar_consulta("SELECT id FROM cursos WHERE profesor_id = ?", (profesor_a_eliminar,))
                if cursos_profesor:
                    print("\033[31mNo se puede eliminar el profesor porque tiene cursos asignados.\033[0m")
                else:
                    db.ejecutar_instruccion(
                        "DELETE FROM profesores WHERE id = ?",(profesor_a_eliminar,))
                    profesores = db.ejecutar_consulta("Select * from profesores")
                    print("\n--- Lista Actualizada de Profesores ---")
                    for prof in profesores:
                        print(f"id: {prof[0]}, Nombre: \033[92m{prof[1]}\033[0m")
                    print("-"*34)
            except Exception as e:
                print("Error al recuperar la lista de profesores:", e)

        #Agregar estudiante a curso
        elif opcion == "8":
            print("\n--- Agregar Estudiante a Curso ---")
            try:
                estudiantes = db.ejecutar_consulta("SELECT * FROM estudiantes")
                print("Estudiantes:")
                for est in estudiantes:
                    print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[1]}\033[0m, Edad: {est[2]}")
                print("")
                cursos = db.ejecutar_consulta("SELECT * FROM cursos")
                print("Cursos:")
                for curso in cursos:
                    print(f"Curso Id: \033[31m{curso[0]}\033[0m, Nombre: \033[92m{curso[1]}\033[0m")
                print("")
                agregar_estudiante_a_curso = input("Ingrese el ID del estudiante a agregar al curso: ")

                try:
                    estudiante_id = int(agregar_estudiante_a_curso)
                except ValueError:
                    print("El ID del estudiante debe ser un número válido.")
                    continue

                estudiante = db.ejecutar_consulta("SELECT nombre FROM estudiantes WHERE id = ?", (estudiante_id,))
                if not estudiante:
                    print("No existe un estudiante con ese ID.")
                    continue
                try:
                    curso_id = input("Ingrese el ID del curso al que desea agregar al estudiante: ")
                    curso_id = int(curso_id)
                except ValueError:
                    print("El ID del curso debe ser un número válido.")
                    continue
                curso = db.ejecutar_consulta("SELECT nombre FROM cursos WHERE id = ?", (curso_id,))
                if not curso:
                    print("No existe un curso con ese ID.")
                    continue
                # Validar si ya está inscrito
                ya_inscrito = db.ejecutar_consulta(
                    "SELECT 1 FROM inscripciones WHERE estudiante_id = ? AND curso_id = ?",
                    (estudiante_id, curso_id)
                )
                if ya_inscrito:
                    print(f"\033[31mEl estudiante ya está inscrito en ese curso.\033[0m")
                else:
                    db.ejecutar_instruccion(
                        "INSERT INTO inscripciones (estudiante_id, curso_id) VALUES (?, ?)",
                        (estudiante_id, curso_id)
                    )
                    print(f"Estudiante \033[92m{estudiante[0][0]}\033[0m agregado al curso exitosamente: \033[92m{curso[0][0]}\033[0m")
            except Exception as e:
                print("Error al agregar estudiante al curso:", e)
        
        # CREAR CURSO
        elif opcion == "9":
            print("\n--- Crear Curso ---")
            try:
                nombre_curso = input("Nombre del curso: ").strip()
                if not nombre_curso or len(nombre_curso) < 3:
                    print("Nombre inválido.")
                    continue
                semestre = input("Semestre (formato YYYY-1 o YYYY-2): ").strip()
                if not validar_semestre(semestre):
                    print("Formato de semestre inválido.")
                    continue
                profesores = db.ejecutar_consulta("SELECT id, nombre FROM profesores")
                if not profesores:
                    print("Debe crear un profesor antes de crear cursos.")
                    continue
                print("Profesores disponibles:")
                for p in profesores:
                    print(f"Profesor Id: {p[0]}, Nombre: {p[1]}")
                try:
                    profesor_id = int(input("Ingrese el ID del profesor responsable: "))
                except ValueError:
                    print("ID inválido.")
                    continue
                existe_prof = [p for p in profesores if p[0] == profesor_id]
                if not existe_prof:
                    print("No existe un profesor con ese ID.")
                    continue
                # Intentar insertar considerando que la tabla tenga columna semestre
                try:
                    db.ejecutar_instruccion(
                        "INSERT INTO cursos (nombre, semestre, profesor_id) VALUES (?, ?, ?)",
                        (nombre_curso.capitalize(), semestre, profesor_id)
                    )
                except Exception as e:
                    # fallback por si la tabla aún no tiene semestre
                    if 'column' in str(e).lower() and 'semestre' in str(e).lower():
                        print("La columna 'semestre' no existe en la tabla 'cursos'. Ejecute: ALTER TABLE cursos ADD semestre NVARCHAR(10);")
                    else:
                        print("Error al crear el curso:", e)
            except Exception as e:
                print("Error al procesar la creación del curso:", e)
                # CREAR PROFESOR 
        elif opcion == "10":
            print("\n--- Crear Profesor ---")
            try:
                nombre_prof = input("Nombre del profesor: ").strip()
                if not nombre_prof or len(nombre_prof) <3: 
                    print("nombre invalidp")
                    continue 
                db.ejecutar = nombre_prof.capitalize()
                db.ejecutar_instruccion(
                    "INSERT INTO profesores (nombre) VALUES (?)",
                    (nombre_prof,) 
                )
            except Exception as e: 
                print("Error al crear el profesor:", e) 
        # LISTAR CURSOS (DETALLE) 
        elif opcion == "11":
            print("\n--- Lista de Cursos (Detalle) ---")
            try:
                    cursos = db.ejecutar_consulta("SELECT id, nombre, semestre, profesor_id FROM cursos")
                    tiene_semestre = True
            except Exception:
                cursos = db.ejecutar_consulta("SELECT id, nombre, profesor_id FROM cursos")
                tiene_semestre = False
                profesores = {p[0]: p[1] for p in db.ejecutar_consulta("SELECT id, nombre FROM profesores")}
                if not cursos:
                    print("No hay cursos registrados.")
                for c in cursos:
                    if tiene_semestre:
                        cid, nombre, semestre, pid = c
                        prof_nombre = profesores.get(pid, 'Sin profesor')
                        print(f"Curso Id: \033[31m{cid}\033[0m, Nombre: \033[92m{nombre}\033[0m, Semestre: {semestre}, Profesor: {prof_nombre}")
                    else:
                        cid, nombre, pid = c
                        prof_nombre = profesores.get(pid, 'Sin profesor')
                        print(f"Curso Id: \033[31m{cid}\033[0m, Nombre: \033[92m{nombre}\033[0m, Profesor: {prof_nombre}")
            except Exception as e:
                print("Error al recuperar la lista de cursos:", e)

        # LISTAR ESTUDIANTES POR CURSO
        elif opcion == "12":
            print("\n--- Estudiantes por Curso ---")
            try:
                cursos = db.ejecutar_consulta("SELECT id, nombre FROM cursos")
                if not cursos:
                    print("No hay cursos.")
                    continue
                for c in cursos:
                    print(f"Curso Id: {c[0]}, Nombre: {c[1]}")
                try:
                    curso_target = int(input("Ingrese el ID del curso: "))
                except ValueError:
                    print("ID invÃ¡lido.")
                    continue
                existe = [c for c in cursos if c[0] == curso_target]
                if not existe:
                    print("Curso no encontrado.")
                    continue
                insc = db.ejecutar_consulta("SELECT estudiante_id FROM inscripciones WHERE curso_id = ?", (curso_target,))
                if not insc:
                    print("No hay estudiantes inscritos en este curso.")
                    continue
                est_ids = [i[0] for i in insc]
                estudiantes = db.ejecutar_consulta("SELECT id, nombre, edad FROM estudiantes")
                print(f"\nEstudiantes inscritos en {existe[0][1]}:")
                for e in estudiantes:
                    if e[0] in est_ids:
                        print(f" - Id: {e[0]} Nombre: {e[1]} Edad: {e[2]}")
            except Exception as e:
                print("Error al listar estudiantes por curso:", e)


                
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
