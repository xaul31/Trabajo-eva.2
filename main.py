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