import hashlib
import re
import oracledb
from dotenv import load_dotenv
import os
import pwinput

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