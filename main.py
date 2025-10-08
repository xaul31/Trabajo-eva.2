import hashlib
from time import time
import oracledb
import os
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
            time.sleep(0.6)
            clear = lambda: os.system('cls')
            clear()
            return True
        else:
            restantes = MAX_INTENTOS - intento
            print(f"\033[31mCredenciales inválidas. Intentos restantes: {restantes}\033[0m")
            if restantes:
                time.sleep(min(1.5 * intento, 4))

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

    