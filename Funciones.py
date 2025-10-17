import oracledb
import os
def mostrar_menu():
    print("\n--- MENÚ PRINCIPAL ---")
    print("1. Listar estudiantes")
    print("2. Agregar estudiante")
    print("3. Buscar estudiante por nombre")
    print("4. Eliminar estudiante por ID")
    print("5. Modificar estudiante por ID")
    print("6. Listar profesores y sus cursos")
    print("7. Eliminar profesor por ID")
    print("8. Agregar estudiante a curso")
    print("9. Crear curso")
    print("10. Crear profesor")
    print("11. Listar cursos (detalle)")
    print("12. Listar estudiantes por curso")
    print("13. Salir")


#OPCION 4 ELIMINAR ESTUDIANTE POR ID
def borrarEstudiante(db):
    estudiantes = db.ejecutar_consulta("""
        SELECT id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento,
               TRUNC(MONTHS_BETWEEN(TRUNC(SYSDATE), fecha_nacimiento) / 12) AS edad
        FROM Estudiante
        ORDER BY id_estudiante asc
    """)
    inscripciones = db.ejecutar_consulta("SELECT id_estudiante, id_curso FROM Inscripcion")
    cursos = db.ejecutar_consulta("SELECT id_curso, nombre FROM Curso")
    
    print("\n--- Lista Actualizada de Estudiantes ---")
    for est in estudiantes:
        cursos_ids = [i[1] for i in inscripciones if i[0] == est[0]]
        cursos_nombres = [c[1] for c in cursos if c[0] in cursos_ids]
        cursos_str = ', '.join(cursos_nombres) if cursos_nombres else 'Sin cursos'
        print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[2]} {est[3]}\033[0m, Edad: {est[6]}, RUT: {est[1]}, Cursos: {cursos_str}")
    print("-----------------------------")
    
    try:
        estudiante_a_eliminar = int(input("Ingrese el ID del estudiante a eliminar: "))
        confirm = input(f"¿Desea eliminar también todas las inscripciones del estudiante {estudiante_a_eliminar}? (S/N): ").strip().upper()
        if confirm != "S":
            print("Operación cancelada.")
            return

        try:
            # Primero eliminamos las inscripciones asociadas
            db.ejecutar_instruccion(
                "DELETE FROM Inscripcion WHERE id_estudiante = :id",
                {"id": estudiante_a_eliminar}
            )
            # Luego eliminamos al estudiante
            db.ejecutar_instruccion(
                "DELETE FROM Estudiante WHERE id_estudiante = :id",
                {"id": estudiante_a_eliminar}
            )
            print("\033[92mEstudiante y sus inscripciones eliminadas.\033[0m")

        except oracledb.DatabaseError as e:
            print("\033[31mError al eliminar estudiante:\033[0m", e)

        # mostrar lista actualizada
        estudiantes = db.ejecutar_consulta("""
            SELECT id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento,
                   TRUNC(MONTHS_BETWEEN(TRUNC(SYSDATE), fecha_nacimiento) / 12) AS edad
            FROM Estudiante
            ORDER BY id_estudiante asc
        """)
        print("\n--- Lista Actualizada de Estudiantes ---")
        for est in estudiantes:
            print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[2]} {est[3]}\033[0m, Edad: {est[6]}, RUT: {est[1]}\033[0m")
        print("-----------------------------")
        
    except ValueError:
        print("\033[31mID inválido. Debe ser un número.\033[0m")

#OPCION 3 BUSCAR ESTUDIANTE POR NOMBRE
def agregarEstudiante(db):
    nombre = input("Ingrese el nombre del estudiante a buscar: ").strip()
    if not nombre:
        print("\033[31mEl nombre no puede estar vacío.\033[0m")
        return
    nombre = nombre.capitalize()
    try:
        estudiantes = db.ejecutar_consulta("""
            SELECT id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento,
                           TRUNC(MONTHS_BETWEEN(TRUNC(SYSDATE), fecha_nacimiento) / 12) AS edad
                    FROM Estudiante
                    WHERE UPPER(nombre) LIKE UPPER(:nombre)
                """, {"nombre": f"{nombre}%"})
        if estudiantes:
            print("\n--- Resultados de la Búsqueda ---")
        for est in estudiantes:
            print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[2]} {est[3]}\033[0m, Edad: {est[6]}, RUT: {est[1]}")
        else:
            print("\033[31mNo se encontraron estudiantes con ese nombre.\033[0m")
    except Exception as e:
                print("\033[31mError al buscar estudiantes:\033[0m", e)

def listarEstudiantes(db):
    estudiantes = db.ejecutar_consulta("""
                SELECT id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento,
                       TRUNC(MONTHS_BETWEEN(TRUNC(SYSDATE), fecha_nacimiento) / 12) AS edad
                FROM Estudiante
                ORDER BY id_estudiante asc
            """)
    inscripciones = db.ejecutar_consulta("SELECT id_estudiante, id_curso FROM Inscripcion")
    cursos = db.ejecutar_consulta("SELECT id_curso, nombre FROM Curso")
    clear = lambda: os.system('cls')
    clear()
    print("--- Lista de Estudiantes  ---")
    for est in estudiantes:
        cursos_ids = [i[1] for i in inscripciones if i[0] == est[0]]
        cursos_nombres = [c[1] for c in cursos if c[0] in cursos_ids]
        cursos_str = ', '.join(cursos_nombres) if cursos_nombres else 'Sin cursos'
        print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[2]} {est[3]}\033[0m, Edad: {est[6]}, RUT: {est[1]}, Cursos: {cursos_str}")
    print("")
    print("Estudiantes totales: \033[92m{}\033[0m".format(len(estudiantes)))