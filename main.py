import oracledb
import os
from dotenv import load_dotenv

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

db = ConexionBD()
db.conectar()