import hashlib
import re
import oracledb
from dotenv import load_dotenv
import os
import pwinput
from datetime import datetime
load_dotenv()

# ================= Utilidades =================

def _hash_password(raw_password: str, salt: str) -> str:
    return hashlib.sha256((salt + raw_password).encode('utf-8')).hexdigest()
def validar_rut(rut):
    return bool(re.match(r"^\d{1,2}\.\d{3}\.\d{3}-[0-9kK]$", rut))
def validar_correo(correo):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo))
def validar_fecha(fecha):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", fecha))
def validar_semestre(valor: str) -> bool:
    """Valida formato de semestre esperado: YYYY-1 o YYYY-2"""
    if not valor or len(valor) != 6:
        return False
    partes = valor.split('-')
    if len(partes) != 2:
        return False
    anio, tramo = partes
    if not (anio.isdigit() and len(anio) == 4):
        return False
    if tramo not in ("1", "2"):
        return False
    return True
# ================= Menú =================
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

# ================= Login ============================

def login():

    load_dotenv()
    admin_user = os.getenv("ADMIN_USER")
    admin_salt = os.getenv("ADMIN_SALT", "default_salt")
    admin_hash = os.getenv("ADMIN_PASSWORD_HASH")

    if not admin_user or not admin_hash:
        admin_user = admin_user or "admin"
        admin_hash = _hash_password("admin", admin_salt)
        print("\033[33m[AVISO] Falta configuración segura de login (.env). Usando credenciales por defecto admin/admin. Cambie esto pronto.\033[0m")

    MAX_INTENTOS = 3
    print("=== SISTEMA ACADEMICO DE INSCRIPCION ===")
    for intento in range(1, MAX_INTENTOS + 1):
        usuario = input("Usuario: ").strip()
        password = pwinput.pwinput("Contraseña: ").strip()
        if usuario == admin_user and _hash_password(password, admin_salt) == admin_hash:
            print("\033[92mLogin exitoso.\033[0m")
            clear = lambda: os.system('cls')
            clear()
            return True
        else:
            restantes = MAX_INTENTOS - intento
            print(f"\033[31mCredenciales inválidas. Intentos restantes: {restantes}\033[0m")
            if restantes:
                print("\033[31mDemasiados intentos fallidos. Saliendo...\033[0m")
    input("Presione Enter para salir...")
    return False

# ================= Conexión a la BD =================

class ConexionBD:

    def __init__(self):
        self.servidor = os.getenv("DB_SERVER")
        self.base_datos = os.getenv("DB_NAME")
        self.usuario = os.getenv("DB_USER")
        self.contrasena = os.getenv("DB_PASSWORD")
        self.conexion = None

    def conectar(self):
        try:
            dsn = f"{self.servidor}/{self.base_datos}"
            self.conexion = oracledb.connect(
                user=self.usuario,
                password=self.contrasena,
                dsn=dsn
            )
            clear = lambda: os.system('cls')
            clear()
            print("\033[92mConexión exitosa a Oracle.\033[0m")
        except Exception as e:
            print("\033[31mError al conectar a la base de datos:\033[0m", e)



    def cerrar_conexion(self):
        if self.conexion:
            self.conexion.close()
            print("\033[92mConexión cerrada.\033[0m")


    def ejecutar_consulta(self, consulta, parametros=()):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(consulta, parametros)
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            return []
    

    def ejecutar_instruccion(self, consulta, parametros=()):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(consulta, parametros)
            self.conexion.commit()
            cursor.close()
            print("Instrucción ejecutada correctamente.")
        except Exception as e:
            print("Error al ejecutar la instrucción:", e)
            self.conexion.rollback()
            

# ================= Funciones del Menú =================

#OPCION 1 LISTAR ESTUDIANTES
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

#OPCION 2 AGREGAR ESTUDIANTE
def agregarEstudiante(db):
    while True:
        try:
            nombre = input("Ingrese el nombre del estudiante: ").strip()
            print("Formato: xx.xxx.xxx-x (con puntos y guion)")
            rut = input("Ingrese el rut del estudiante: ").strip()

            if not nombre or len(nombre) < 3:
                print("\033[31mEl nombre no puede estar vacío y debe tener al menos 3 caracteres.\033[0m")
                continue
            if not validar_rut(rut):
                print("\033[31mEl RUT ingresado no tiene un formato válido.\033[0m")
                continue

            apellido = input("Ingrese el apellido del estudiante: ").strip()
            correo = input("Ingrese el correo del estudiante: ").strip()
            if not validar_correo(correo):
                print("\033[31mEl correo ingresado no tiene un formato válido.\033[0m")
                continue

            fecha_nacimiento = input("Ingrese la fecha de nacimiento del estudiante (YYYY-MM-DD): ").strip()
            if not validar_fecha(fecha_nacimiento):
                print("\033[31mLa fecha de nacimiento no tiene un formato válido (YYYY-MM-DD).\033[0m")
                continue

            nombre = nombre.capitalize()
            fecha_nac_date = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()

            db.ejecutar_instruccion(
                "INSERT INTO Estudiante (id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento) "
                "VALUES (seq_estudiante.NEXTVAL, :rut, :nombre, :apellido, :correo, :fecha_nacimiento)",
                {
                    "rut": rut,
                    "nombre": nombre,
                    "apellido": apellido,
                    "correo": correo,
                    "fecha_nacimiento": fecha_nac_date
                }
            )

            # Mostrar lista actualizada
            try:
                estudiantes = db.ejecutar_consulta("""
                    SELECT id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento,
                           TRUNC(MONTHS_BETWEEN(TRUNC(SYSDATE), fecha_nacimiento) / 12) AS edad
                    FROM Estudiante
                    ORDER BY id_estudiante asc
                """)
                clear = lambda: os.system('cls')
                clear()
                print("\n--- Lista Actualizada de Estudiantes ---")
                for est in estudiantes:
                    print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[2]} {est[3]}\033[0m, Edad: {est[6]}, RUT: {est[1]}")
            except Exception as e:
                print("\033[31mError al recuperar la lista de estudiantes:\033[0m", e)

            break  # salir tras inserción exitosa

        except KeyboardInterrupt:
            print("\nSaliendo")
            break
        except Exception as e:
            print("\033[31mError al crear el estudiante:\033[0m", e)
            # repetir ingreso
            continue

#OPCION 3 BUSCAR ESTUDIANTE POR NOMBRE
def buscarEstudiante(db):
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


#OPCION 5 MODIFICAR ESTUDIANTE POR ID
def modificarEstudiante(db):
    try:
        listarEstudiantes(db)

        id_txt = input("Ingrese el ID del estudiante a modificar: ").strip()
        if not id_txt.isdigit():
            print("\033[31mEl ID debe ser numérico.\033[0m")
            return
        id_estudiante = int(id_txt)

        fila = db.ejecutar_consulta("""
            SELECT id_estudiante, rut, nombre, apellido, correo, TO_CHAR(fecha_nacimiento, 'YYYY-MM-DD')
            FROM Estudiante
            WHERE id_estudiante = :id
        """, {"id": id_estudiante})

        if not fila:
            print("\033[31mNo existe un estudiante con ese ID.\033[0m")
            return

        _, rut, nombre, apellido, correo, fecha = fila[0]
        print(f"Actual -> RUT={rut}, Nombre={nombre}, Apellido={apellido}, Correo={correo}, Fecha Nac.={fecha}")

        dato = input(f"RUT (xx.xxx.xxx-x) [{rut}] (Enter para mantener): ").strip()
        if dato != "":
            if not validar_rut(dato):
                print("\033[31mRUT inválido.\033[0m")
                return
            existe = db.ejecutar_consulta(
                "SELECT 1 FROM Estudiante WHERE rut = :rut AND id_estudiante <> :id",
                {"rut": dato, "id": id_estudiante}
            )
            if existe:
                print("\033[31mEl RUT ingresado ya está registrado por otro estudiante.\033[0m")
                return
            rut = dato

        dato = input(f"Nombre [{nombre}] (Enter para mantener): ").strip()
        if dato != "":
            if len(dato) < 3:
                print("\033[31mEl nombre debe tener al menos 3 caracteres.\033[0m")
                return
            nombre = dato.capitalize()

        dato = input(f"Apellido [{apellido}] (Enter para mantener): ").strip()
        if dato != "":
            apellido = dato

        dato = input(f"Correo [{correo}] (Enter para mantener): ").strip()
        if dato != "":
            if not validar_correo(dato):
                print("\033[31mCorreo inválido.\033[0m")
                return
            correo = dato

        dato = input(f"Fecha de nacimiento (YYYY-MM-DD) [{fecha}] (Enter para mantener): ").strip()
        if dato != "":
            if not validar_fecha(dato):
                print("\033[31mFecha inválida (YYYY-MM-DD).\033[0m")
                return
            fecha = dato

        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()

        db.ejecutar_instruccion("""
            UPDATE Estudiante
               SET rut = :rut,
                   nombre = :nombre,
                   apellido = :apellido,
                   correo = :correo,
                   fecha_nacimiento = :fecha
             WHERE id_estudiante = :id
        """, {
            "rut": rut,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "fecha": fecha_obj,
            "id": id_estudiante
        })

        print("\033[92mEstudiante actualizado correctamente.\033[0m")

    except KeyboardInterrupt:
        print("\nSaliendo")
    except Exception as e:
        print("\033[31mError al actualizar estudiante:\033[0m", e)




#OPCION 6 LISTAR PROFESORES Y SUS CURSOS
def listarProfesoresYCursos(db): #<-- incompleto
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


#OPCION 7 ELIMINAR PROFESOR POR ID
def borrarProfesor(db): #<-- incompleto
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


#opcion 8 AGREGAR ESTUDIANTE A CURSO
def agregarEstudianteACurso(db): #<-- incompleto
    print("\n--- Agregar Estudiante a Curso ---")
    while True:
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


#OPCION 9 CREAR CURSO
def crearCurso(db): #<-- incompleto
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

#OPCION 10 CREAR PROFESOR
def crearProfesor(db): #<-- incompleto
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

#OPCION 11 LISTAR CURSOS (DETALLE)
def listarCursosDetalle(db): #<-- incompleto
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

#OPCION 12 LISTAR ESTUDIANTES POR CURSO
def listarEstudiantesPorCurso(db): #<-- incompleto
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