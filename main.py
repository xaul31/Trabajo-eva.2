import hashlib
import os
import oracledb
from dotenv import load_dotenv
import pwinput

load_dotenv()

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

# ================= Utilidades =================
def _hash_password(raw_password: str, salt: str) -> str:
    return hashlib.sha256((salt + raw_password).encode('utf-8')).hexdigest()

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
            estudiantes = db.ejecutar_consulta("SELECT * FROM estudiantes")
            inscripciones = db.ejecutar_consulta("SELECT estudiante_id, curso_id FROM inscripciones")
            cursos = db.ejecutar_consulta("SELECT id, nombre FROM cursos")
            clear = lambda: os.system('cls')
            clear()
            print("--- Lista de Estudiantes  ---")
            for est in estudiantes:
                cursos_ids = [i[1] for i in inscripciones if i[0] == est[0]]
                cursos_nombres = [c[1] for c in cursos if c[0] in cursos_ids]
                cursos_str = ', '.join(cursos_nombres) if cursos_nombres else 'Sin cursos'
                print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[1]}\033[0m, Edad: {est[2]}, RUT: {est[3]}, Cursos: {cursos_str}")
            print("")
            print("Estudiantes totales: \033[92m{}\033[0m".format(len(estudiantes)))
        #AGREGAR ESTUDIANTE
        elif opcion == "2":
            try:
                nombre = input("Ingrese el nombre del estudiante: ").strip()
                if not nombre or len(nombre) < 3:
                    print("\033[31mEl nombre no puede estar vacío y debe tener al menos 3 caracteres.\033[0m")
                    continue
                nombre = nombre.capitalize()
                edad = int(input("Ingrese la edad del estudiante: "))
                if edad < 15 or edad > 99:
                    print("La edad debe estar entre 15 y 99 años.")
                    continue
                db.ejecutar_instruccion(
                    "INSERT INTO estudiantes (nombre, edad) VALUES (?, ?)",
                    (nombre, edad)
                )
                try:
                    estudiantes = db.ejecutar_consulta("SELECT * FROM estudiantes")
                    clear = lambda: os.system('cls')
                    clear()
                    print("\n--- Lista Actualizada de Estudiantes ---")
                    for est in estudiantes:
                        print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[1]}\033[0m, Edad: {est[2]}")
                except Exception as e:
                    print("\033[31mError al recuperar la lista de estudiantes:\033[0m", e)
            except ValueError:
                print("\033[31mEdad inválida. Debe ser un número.\033[0m")
        #Buscar Estudiante por nombre
        elif opcion == "3":
            nombre = input("Ingrese el nombre del estudiante a buscar: ").strip()
            if not nombre:
                print("\033[31mEl nombre no puede estar vacío.\033[0m")
                continue
            nombre = nombre.capitalize()
            try:
                estudiantes = db.ejecutar_consulta("SELECT * FROM estudiantes WHERE nombre LIKE ?",(f"{nombre}%",))
                if estudiantes:
                    print("\n--- Resultados de la Búsqueda ---")
                    for est in estudiantes:
                        print(f"id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[1]}\033[0m, Edad: {est[2]}, RUT: {est[3]}")
                else:
                    print("\033[31mNo se encontraron estudiantes con ese nombre.\033[0m")
            except Exception as e:
                print("\033[31mError al buscar estudiantes:\033[0m", e)
        #Eliminar Estudiante
        elif opcion == "4":
            estudiantes = db.ejecutar_consulta("SELECT * FROM estudiantes")
            print("--- Lista de Estudiantes ---")
            for est in estudiantes:
                print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[1]}\033[0m, Edad: {est[2]}")
            print("-----------------------------")
            try:
                estudiante_a_eliminar = int(input("Ingrese el ID del estudiante a eliminar: "))
                db.ejecutar_instruccion(
                    "DELETE FROM estudiantes WHERE id = ?",(estudiante_a_eliminar,))
                estudiantes = db.ejecutar_consulta("SELECT * FROM estudiantes")
                print("\n--- Lista Actualizada de Estudiantes ---")
                for est in estudiantes:
                    print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[1]}\033[0m, Edad: {est[2]}")
                print("-----------------------------")
            except ValueError:
                print("\033[31mID inválido. Debe ser un número.\033[0m")

             
        #MODIFICAR ESTUDIANTE POR ID
        elif opcion == "5":
            print("\n--- Modificar Estudiante ---")
            try:
                edad = int(input("Ingrese la edad del estudiante: "))
                id = input("Ingrese el ID del estudiante a modificar: ").strip()
                if not id.isdigit():
                    print("El ID debe ser un número válido.")
                    continue
                if edad < 15 or edad > 99:
                    print("La edad debe estar entre 15 y 99 años.")
                    continue
                
                for est in estudiantes:
                    print(f"id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[1]}\033[0m, Edad: {est[2]}, RUT: {est[3]}")
            except ValueError:
                print("Edad inválida. Debe ser un número.")
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
                nombre_profesor = input("Nombre del profesor: ").strip()
                if not nombre_profesor or len(nombre_profesor) <3: 
                    print("nombre invalidp")
                    continue 
                db.ejecutar = nomb_prof.capitalize()
                db.ejecutar_instruccion(
                    "INSERT INTO profesores (nombre) VALUES (?)",
                    (nombre_profe,) 
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
