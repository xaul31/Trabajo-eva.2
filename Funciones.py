from hashlib import sha256
from re import match
import oracledb
from dotenv import load_dotenv
from os import getenv,system
from pwinput import pwinput
from datetime import datetime
load_dotenv()

# ================= Utilidades =================

def _hash_password(raw_password: str, salt: str) -> str:
    return sha256((salt + raw_password).encode('utf-8')).hexdigest()
def validar_rut(rut):# Formato: xx.xxx.xxx-x
    return bool(match(r"^\d{1,2}\.\d{3}\.\d{3}-[0-9kK]$", rut))
def validar_correo(correo):#Formato: local@dominio.com
    return bool(match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo))
def validar_fecha(fecha):#
    return bool(match(r"^\d{4}-\d{2}-\d{2}$", fecha))
def validar_semestre(valor: str) -> bool:#funcion para validar semestre
    """Valida formato de semestre esperado: YYYY-1 o YYYY-2"""
    if not valor or len(valor) != 6:#validar longitud
        return False
    partes = valor.split('-')#dividir por guion
    if len(partes) != 2:#validar que haya dos partes
        return False
    anio, tramo = partes#asignar partes a variables
    if not (anio.isdigit() and len(anio) == 4):#validar año
        return False
    if tramo not in ("1", "2"):#validar tramo(primer o segundo semestre)
        return False#validar que el tramo sea 1 o 2
    return True#retornar True si es válido
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
    print("8. Agregar profesor")
    print("9. Agregar estudiante a curso")
    print("10. Crear curso")
    print("11. Listar cursos")
    print("12. Listar estudiantes por curso")
    print("13. Salir")

# ================= Login ============================

def login():#funcion login

    load_dotenv()#cargar variables de entorno desde .env
    admin_user = getenv("ADMIN_USER")#usuario admin desde .env
    admin_salt = getenv("ADMIN_SALT", "default_salt")#salto para hash de contraseña
    admin_hash = getenv("ADMIN_PASSWORD_HASH")#hash de contraseña admin desde .env

    if not admin_user or not admin_hash:#si faltan variables de entorno, usar credenciales por defecto
        admin_user = admin_user or "admin"#usuario por defecto
        admin_hash = _hash_password("admin", admin_salt)#hash de contraseña por defecto
        print("\033[33m[AVISO] Falta configuración segura de login (.env). Usando credenciales por defecto admin/admin. Cambie esto pronto.\033[0m")

    MAX_INTENTOS = 3# número máximo de intentos de login
    print("=== SISTEMA ACADEMICO DE INSCRIPCION ===")
    for intento in range(1, MAX_INTENTOS + 1):#bucle de intentos de login en el rango de 1 a MAX_INTENTOS
        usuario = input("Usuario: ").strip()#input usuario y quitar espacios
        password = pwinput("Contraseña: ").strip()#input contraseña oculta y quitar espacios
        if usuario == admin_user and _hash_password(password, admin_salt) == admin_hash:#validar credenciales
            print("\033[92mLogin exitoso.\033[0m")#imprimir mensaje de éxito
            clear = lambda: system('cls')#limpiar pantalla
            clear()
            return True# retornar True si login exitoso
        else:#si credenciales inválidas
            restantes = MAX_INTENTOS - intento# calcular intentos restantes
            print(f"\033[31mCredenciales inválidas. Intentos restantes: {restantes}\033[0m")#imprimir mensaje de error
            if restantes:#si quedan intentos
                print("\033[31mDemasiados intentos fallidos. Saliendo...\033[0m")
    return False # retornar False si login falla tras MAX_INTENTOS

# ================= Conexión a la BD =================

class ConexionBD:#clase para manejar la conexión a la base de datos Oracle

    def __init__(self):#inicializar la conexión
        self.servidor = getenv("DB_SERVER")#servidor desde .env
        self.base_datos = getenv("DB_NAME")#base de datos desde .env
        self.usuario = getenv("DB_USER")#usuario desde .env
        self.contrasena = getenv("DB_PASSWORD")#contraseña desde .env
        self.conexion = None#inicializar conexión como None

    def conectar(self):#conectar a la base de datos
        try:#capturar errores de conexión
            dsn = f"{self.servidor}/{self.base_datos}"#formatear dsn
            self.conexion = oracledb.connect(#conectar a la base de datos Oracle
                user=self.usuario,
                password=self.contrasena,
                dsn=dsn
            )
            clear = lambda: system('cls')#limpiar pantalla
            clear()
            print("\033[92mConexión exitosa a Oracle.\033[0m")#imprimir mensaje de éxito
        except Exception as e:
            print("\033[31mError al conectar a la base de datos:\033[0m", e)#imprimir mensaje de error



    def cerrar_conexion(self):#cerrar la conexión a la base de datos
        if self.conexion:
            self.conexion.close()
            print("\033[92mConexión cerrada.\033[0m")


    def ejecutar_consulta(self, consulta, parametros=()):#ejecutar una consulta SELECT
        try:#capturar errores de consulta
            cursor = self.conexion.cursor()#crear cursor
            cursor.execute(consulta, parametros)#ejecutar consulta con parámetros
            resultados = cursor.fetchall()#obtener todos los resultados
            cursor.close()#cerrar cursor
            return resultados#retornar resultados como lista de tuplas
        except Exception as e:#capturar error de consulta
            print("Error al ejecutar la consulta:", e)
            return []#retornar lista vacía en caso de error
    

    def ejecutar_instruccion(self, consulta, parametros=()):#ejecutar una instrucción INSERT, UPDATE o DELETE
        try:#capturar errores de instrucción
            cursor = self.conexion.cursor()#crear cursor
            cursor.execute(consulta, parametros)#ejecutar instrucción con parámetros
            self.conexion.commit()#confirmar cambios
            cursor.close()#cerrar cursor
            print("Instrucción ejecutada correctamente.")
        except Exception as e:#capturar error de instrucción
            print("Error al ejecutar la instrucción:", e)
            self.conexion.rollback()#revertir cambios en caso de error




#herencia
class Persona:  # clase base
    def __init__(self, rut, nombre, apellido, correo):
        self.rut = rut
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()


class estudiante(Persona):  # hereda de Persona
    # tiene id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento, edad, cursos
    def __init__(self, id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento, edad=None, cursos=None):
        super().__init__(rut, nombre, apellido, correo)  # inicializa campos comunes
        self.id_estudiante = id_estudiante
        self.fecha_nacimiento = fecha_nacimiento
        self.edad = edad
        self.cursos = cursos or []  # lista de nombres de cursos

    # polimorfismo
    def presentacion(self):
        cursos_str = ', '.join(self.cursos) if hasattr(self, 'cursos') and self.cursos else 'Sin cursos'
        return (
            f"Estudiante Id: \033[31m{self.id_estudiante}\033[0m, "
            f"Nombre: \033[92m{self.nombre_completo()}\033[0m, "
            f"Edad: {self.edad}, correo:{self.correo}, RUT: {self.rut}, Cursos: {cursos_str}"
        )


class profesor(Persona):  # hereda de Persona
    # tiene id_profesor, rut, nombre, apellido, correo, cursos
    def __init__(self, id_profesor, rut, nombre, apellido, correo, cursos=None):
        super().__init__(rut, nombre, apellido, correo)  # inicializa campos comunes
        self.id_profesor = id_profesor
        self.cursos = cursos or []  # lista de nombres de cursos

    # polimorfismo
    def presentacion(self):
        if self.cursos:
            return "\n".join([
                f"Profesor id: {self.id_profesor}, Nombre: \033[92m{self.nombre_completo()}\033[0m, Curso: {c}, Correo: {self.correo}"
                for c in self.cursos
            ])
        return f"Profesor id: {self.id_profesor}, Nombre: \033[92m{self.nombre_completo()}\033[0m, Curso: Sin curso asignado, Correo: {self.correo}"


class curso:  # sin cambios funcionales
    # curso tiene id_curso, codigo, nombre, semestre, id_profesor
    def __init__(self, id_curso, codigo, nombre, semestre, id_profesor):
        self.id_curso = id_curso
        self.codigo = codigo
        self.nombre = nombre
        self.semestre = semestre
        self.id_profesor = id_profesor

    def presentacion(self, profesor_nombre=None, inscritos=0):
        prof = profesor_nombre or "Sin profesor"
        sem = self.semestre if self.semestre else "Sin semestre"
        return f"Curso Id: \033[31m{self.id_curso}\033[0m, Nombre: \033[92m{self.nombre}\033[0m, Semestre: {sem}, Profesor: {prof}, Inscritos: {inscritos}"


class inscripcion:  # sin cambios
    def __init__(self, id_inscripcion, id_estudiante, id_curso):
        self.id_inscripcion = id_inscripcion
        self.id_estudiante = id_estudiante
        self.id_curso = id_curso
def cursos_por_estudiante(db):
    inscripciones = db.ejecutar_consulta("SELECT id_estudiante, id_curso FROM Inscripcion")#lista de tuplas (id_estudiante, id_curso)
    cursos = db.ejecutar_consulta("SELECT id_curso, nombre FROM Curso")#lista de tuplas (id_curso, nombre)
    mapa_de_cursos = {c[0]: c[1] for c in cursos}# mapa de id_curso a nombre se agarra el id y el nombre de cada curso recorrido con un for
    por_estudiante = {}# mapa de id_estudiante a lista de nombres de cursos
    for id_estudiante, id_curso in inscripciones:# recorrer las inscripciones
        por_estudiante.setdefault(id_estudiante, []).append(mapa_de_cursos.get(id_curso, str(id_curso)))
    return por_estudiante

def fila_estudiante(fila, cursos_mapa):# convierte una fila de consulta en un objeto estudiante
    #lista: id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento, edad
    id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento, edad = fila
    return estudiante(id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento, edad=edad, cursos=cursos_mapa.get(id_estudiante, []))
    #retorna un objeto estudiante con los datos de la fila y los cursos del mapa
# ================= Funciones del Menú =================

#OPCION 1 LISTAR ESTUDIANTES
def listarEstudiantes(db):#funcion listar estudiantes
    estudiantes_consulta = db.ejecutar_consulta("""
                SELECT id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento,
                       TRUNC(MONTHS_BETWEEN(TRUNC(SYSDATE), fecha_nacimiento) / 12) AS edad
                FROM Estudiante
                ORDER BY id_estudiante asc
            """)#sqlquery para obtener los estudiantes
    cursos_mapa = cursos_por_estudiante(db)#funcion que retorna un mapa de id_estudiante a lista de nombres de cursos
    clear = lambda: system('cls')#limpiar pantalla
    clear()
    print("--- Lista de Estudiantes  ---")
    estudiantes_objetos = [ fila_estudiante(r, cursos_mapa) for r in estudiantes_consulta ]#array de objetos estudiante, cada fila convertida a objeto estudiante donde r es cada fila de la consulta
    for objeto in estudiantes_objetos:#recorrer los objetos estudiante
        print(objeto.presentacion())#imprimir la presentacion de cada objeto estudiante
    print("")
    print("Estudiantes totales: \033[92m{}\033[0m".format(len(estudiantes_objetos)))#imprimir el total de estudiantes con len para contar los objetos en el array

#OPCION 2 AGREGAR ESTUDIANTE
def agregarEstudiante(db):#funcion agregar estudiante
    while True:#bucle infinito hasta que se agregue correctamente
        try:#try para capturar errores
            nombre = input("Ingrese el nombre del estudiante: ").strip()#input nombre y quitar espacios
            print("Formato: xx.xxx.xxx-x (con puntos y guion)")#indicar formato de rut
            rut = input("Ingrese el rut del estudiante: ").strip()#input rut y quitar espacios

            if not nombre or len(nombre) < 3:#validar nombre no vacío y al menos 3 caracteres
                print("\033[31mEl nombre no puede estar vacío y debe tener al menos 3 caracteres.\033[0m")
                continue# repetir ingreso
            if not validar_rut(rut):#validar formato de rut
                print("\033[31mEl RUT ingresado no tiene un formato válido.\033[0m")
                continue# repetir ingreso

            apellido = input("Ingrese el apellido del estudiante: ").strip()#input apellido y quitar espacios
            correo = input("Ingrese el correo del estudiante: ").strip()#input correo y quitar espacios
            if not validar_correo(correo):#validar formato de correo
                print("\033[31mEl correo ingresado no tiene un formato válido.\033[0m")
                continue# repetir ingreso

            fecha_nacimiento = input("Ingrese la fecha de nacimiento del estudiante (YYYY-MM-DD): ").strip()#input fecha nacimiento y quitar espacios
            if not validar_fecha(fecha_nacimiento):#validar formato de fecha
                print("\033[31mLa fecha de nacimiento no tiene un formato válido (YYYY-MM-DD).\033[0m")
                continue

            nombre = nombre.capitalize()#ajustar nombre a mayúscula inicial
            fecha_nac_date = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()# convertir string a objeto date sea año-mes-dia

            db.ejecutar_instruccion(#insertar estudiante en la base de datos
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

            try:#mostrar lista actualizada de estudiantes
                estudiantes = db.ejecutar_consulta("""
                    SELECT id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento,
                           TRUNC(MONTHS_BETWEEN(TRUNC(SYSDATE), fecha_nacimiento) / 12) AS edad
                    FROM Estudiante
                    ORDER BY id_estudiante asc
                """)#sqlquery para obtener los estudiantes
                clear = lambda: system('cls')#limpiar pantalla
                clear()
                print("\n--- Lista Actualizada de Estudiantes ---")
                for est in estudiantes:#recorrer las filas de estudiantes
                    print(f"Estudiante Id: \033[31m{est[0]}\033[0m, Nombre: \033[92m{est[2]} {est[3]}\033[0m, Edad: {est[6]}, RUT: {est[1]}")
                    #Estudiante Id: 1, Nombre: Nelson Perez, Edad: 20, RUT: 12.345.678-9
            except Exception as e:#capturar error al mostrar lista
                print("\033[31mError al recuperar la lista de estudiantes:\033[0m", e)

            break  # salir tras inserción exitosa

        except KeyboardInterrupt:#capturar ctrl+c para salir
            print("\nSaliendo")
            break
        except Exception as e:
            print("\033[31mError al crear el estudiante:\033[0m", e)
            # repetir ingreso
            continue

#OPCION 3 BUSCAR ESTUDIANTE POR NOMBRE
def buscarEstudiante(db):#funcion buscar estudiante por nombre
    nombre = input("Ingrese el nombre del estudiante a buscar: ").strip()#input nombre y quitar espacios
    if not nombre:#validar nombre no vacío
        print("\033[31mEl nombre no puede estar vacío.\033[0m")
        return# salir de la función
    nombre = nombre.capitalize()#ajustar nombre a mayúscula inicial
    try:#para capturar errores
        estudiantes_consulta = db.ejecutar_consulta("""
            SELECT id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento,
                   TRUNC(MONTHS_BETWEEN(TRUNC(SYSDATE), fecha_nacimiento) / 12) AS edad
            FROM Estudiante
            WHERE UPPER(nombre) LIKE UPPER(:nombre)
                """, {"nombre": f"{nombre}%"})#buscar estudiantes cuyo nombre empiece con el texto ingresado, sin importar mayúsculas/minúsculas
        if estudiantes_consulta:#si se encontraron estudiantes
            cursos_mapa = cursos_por_estudiante(db)#obtener mapa de cursos por estudiante
            print("\n--- Resultados de la Búsqueda ---")
            for r in estudiantes_consulta:#recorrer las filas encontradas
                est_obj = fila_estudiante(r, cursos_mapa)#convertir fila a objeto estudiante 
                print(est_obj.presentacion())#imprimir la presentacion del objeto estudiante
        else:#si no se encontraron estudiantes
            print("\033[31mNo se encontraron estudiantes con ese nombre.\033[0m")#imprimir mensaje de no encontrado
    except Exception as e:#capturar error al buscar estudiantes
        print("\033[31mError al buscar estudiantes:\033[0m", e)



#OPCION 4 ELIMINAR ESTUDIANTE POR ID
def borrarEstudiante(db):#funcion borrar estudiante por id
    estudiantes_consulta = db.ejecutar_consulta("""
        SELECT id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento,
               TRUNC(MONTHS_BETWEEN(TRUNC(SYSDATE), fecha_nacimiento) / 12) AS edad
        FROM Estudiante
        ORDER BY id_estudiante asc
    """)#sqlquery para obtener los estudiantes
    cursos_mapa = cursos_por_estudiante(db)#obtener mapa de cursos por estudiante
    print("\n--- Lista Actualizada de Estudiantes ---")
    for r in estudiantes_consulta:#recorrer las filas de estudiantes
        est_obj = fila_estudiante(r, cursos_mapa)#convertir fila a objeto estudiante
        print(est_obj.presentacion())#imprimir la presentacion del objeto estudiante
    print("-----------------------------")
    try:#capturar errores
        estudiante_a_eliminar = int(input("Ingrese el ID del estudiante a eliminar: "))#input id estudiante a eliminar y convertir a entero
        confirm = input(f"¿Desea eliminar también todas las inscripciones del estudiante {estudiante_a_eliminar}? (S/N): ").strip().upper()#confirmar eliminación de inscripciones
        if confirm != "S":#si no confirma con S
            print("Operación cancelada.")
            return# salir de la función
        try:#eliminar inscripciones y estudiante
            db.ejecutar_instruccion("DELETE FROM Inscripcion WHERE id_estudiante = :id", {"id": estudiante_a_eliminar})#eliminar inscripciones del estudiante
            db.ejecutar_instruccion("DELETE FROM Estudiante WHERE id_estudiante = :id", {"id": estudiante_a_eliminar})#eliminar estudiante
            print("\033[92mEstudiante y sus inscripciones eliminadas.\033[0m")#imprimir mensaje de éxito
        except oracledb.DatabaseError as e:#capturar error de base de datos
            print("\033[31mError al eliminar estudiante:\033[0m", e)#imprimir mensaje de error
    except ValueError:#capturar error de conversión a entero
        print("\033[31mID inválido. Debe ser un número.\033[0m")


#OPCION 5 MODIFICAR ESTUDIANTE POR ID
def modificarEstudiante(db):#funcion modificar estudiante por id
    try:#capturar errores
        listarEstudiantes(db)#listar estudiantes para mostrar la lista actual

        id_a_modificar = input("Ingrese el ID del estudiante a modificar: ").strip()#input id estudiante a modificar y quitar espacios
        if not id_a_modificar.isdigit():#validar que el id sea numérico
            print("\033[31mEl ID debe ser numérico.\033[0m")
            return# salir de la función
        id_estudiante = int(id_a_modificar)#convertir id a entero y almacenar en variable

        fila = db.ejecutar_consulta("""
            SELECT id_estudiante, rut, nombre, apellido, correo, TO_CHAR(fecha_nacimiento, 'YYYY-MM-DD')
            FROM Estudiante
            WHERE id_estudiante = :id
        """, {"id": id_estudiante})#obtener fila del estudiante a modificar

        if not fila:#si no se encontró el estudiante
            print("\033[31mNo existe un estudiante con ese ID.\033[0m")
            return# salir de la función

        id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento = fila[0]#desempaquetar fila
        print(f"Actual -> RUT={rut}, Nombre={nombre}, Apellido={apellido}, Correo={correo}, Fecha Nac.={fecha_nacimiento}")#imprimir datos actuales del estudiante

        cursos_inscritos = db.ejecutar_consulta("""
            SELECT c.id_curso, NVL(c.codigo, '---'), c.nombre
            FROM Curso c
            JOIN Inscripcion i ON i.id_curso = c.id_curso
            WHERE i.id_estudiante = :id
            ORDER BY c.id_curso
        """, {"id": id_estudiante})#obtener cursos inscritos del estudiante

        if cursos_inscritos:#si tiene cursos inscritos
            print("\nCursos en los que está inscrito:")#imprimir cursos inscritos
            for c in cursos_inscritos:#recorrer cursos inscritos
                print(f" - Id curso: {c[0]}, Código: {c[1]}, Nombre: {c[2]}")#imprimir id, código y nombre del curso
            sacar = input("¿Desea sacar a este estudiante de algún curso? (S/N): ").strip().upper()#preguntar si desea sacar al estudiante de algún curso
            if sacar == "S":#si confirma con S
                curso_a_eliminar = input("Ingrese el ID del curso a eliminar (Enter para cancelar): ").strip()#input id curso a eliminar y quitar espacios
                if curso_a_eliminar.isdigit():#si el id es numérico
                    curso_id = int(curso_a_eliminar)#convertir id a entero y almacenar en variable
                    existe_curso = [c for c in cursos_inscritos if c[0] == curso_id]#verificar si el estudiante está inscrito en ese curso
                    #[c for c in cursos_inscritos if c[0] == curso_id] crea una lista con los cursos inscritos cuyo id coincida con el id ingresado
                    if not existe_curso:#si no está inscrito
                        print("\033[31mEl estudiante no está inscrito en ese curso.\033[0m")#imprimir mensaje de error
                    else:#si está inscrito
                        db.ejecutar_instruccion(
                            "DELETE FROM Inscripcion WHERE id_estudiante = :e AND id_curso = :c",
                            {"e": id_estudiante, "c": curso_id}#eliminar inscripción del estudiante en el curso
                        )
                        print("\033[92mEstudiante removido del curso correctamente.\033[0m")#imprimir mensaje de éxito
                else:#si no es numérico
                    print("Operación de eliminación cancelada.")#imprimir mensaje de cancelación
        else:#si no tiene cursos inscritos
            print("\nSin cursos inscritos para este estudiante.")

        dato_rut = input(f"\nRUT (xx.xxx.xxx-x) [{rut}] (Enter para mantener): ").strip()#input nuevo rut y quitar espacios
        if dato_rut != "":#si se ingresó un nuevo rut
            if not validar_rut(dato_rut):#validar formato de rut con regex
                print("\033[31mRUT inválido.\033[0m")#imprimir mensaje de error
                return# salir de la función
            existe = db.ejecutar_consulta(
                "SELECT 1 FROM Estudiante WHERE rut = :rut AND id_estudiante <> :id",
                {"rut": dato_rut, "id": id_estudiante}#selecciona 1 si existe otro estudiante con el mismo rut, excluyendo el actual 
            )
            if existe:#si existe otro estudiante con el mismo rut
                print("\033[31mEl RUT ingresado ya está registrado por otro estudiante.\033[0m")
                return# salir de la función
            rut = dato_rut#actualizar rut

        dato_nombre = input(f"Nombre [{nombre}] (Enter para mantener): ").strip()#input nuevo nombre y quitar espacios
        if dato_nombre != "":#si se ingresó un nuevo nombre
            if len(dato_nombre) < 3:#validar que el nombre tenga al menos 3 caracteres
                print("\033[31mEl nombre debe tener al menos 3 caracteres.\033[0m")
                return# salir de la función
            nombre = dato_nombre.capitalize()#actualizar nombre

        dato_apellido = input(f"Apellido [{apellido}] (Enter para mantener): ").strip()#input nuevo apellido y quitar espacios
        if dato_apellido != "":#si se ingresó un nuevo apellido
            apellido = dato_apellido.capitalize()#actualizar apellido

        dato_correo = input(f"Correo [{correo}] (Enter para mantener): ").strip()#input nuevo correo y quitar espacios
        if dato_correo != "":#si se ingresó un nuevo correo
            if not validar_correo(dato_correo):
                print("\033[31mCorreo inválido.\033[0m")
                return# salir de la función
            correo = dato_correo#actualizar correo

        dato_fecha = input(f"Fecha de nacimiento (YYYY-MM-DD) [{fecha_nacimiento}] (Enter para mantener): ").strip()#input nueva fecha y quitar espacios
        if dato_fecha != "":#si se ingresó una nueva fecha
            if not validar_fecha(dato_fecha):
                print("\033[31mFecha inválida (YYYY-MM-DD).\033[0m")
                return# salir de la función
            fecha_nacimiento = dato_fecha#actualizar fecha y 

        fecha_obj = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()#convertir string a objeto date

        db.ejecutar_instruccion("""
            UPDATE Estudiante
               SET rut = :rut,
                   nombre = :nombre,
                   apellido = :apellido,
                   correo = :correo,
                   fecha_nacimiento = :fecha_nacimiento
             WHERE id_estudiante = :id
        """, {
            "rut": rut,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "fecha_nacimiento": fecha_obj,
            "id": id_estudiante
        })#actualizar estudiante en la base de datos

        print("\033[92mEstudiante actualizado correctamente.\033[0m")#imprimir mensaje de éxito

    except KeyboardInterrupt:#capturar ctrl+c para salir
        print("\nSaliendo")#imprimir mensaje de salida
    except Exception as e:#capturar otros errores
        print("\033[31mError al actualizar estudiante:\033[0m", e)#imprimir mensaje de error




#OPCION 6 LISTAR PROFESORES Y SUS CURSOS
def listarProfesoresYCursos(db):
    try:#capturar errores
        print("\n--- Lista de Profesores y sus Cursos ---")
        profesores_consulta = db.ejecutar_consulta("""
            SELECT id_profesor, rut, nombre, apellido, correo
            FROM Profesor
            ORDER BY id_profesor
        """)#obtener filas de profesores
        cursos_consulta= db.ejecutar_consulta("SELECT id_curso, nombre, id_profesor FROM Curso")#obtener filas de cursos
        cursos_por_prof = {}# mapa de id_profesor a lista de nombres de cursos
        for c in cursos_consulta:#recorrer filas de cursos
            prof_id = c[2]#id_profesor
            cursos_por_prof.setdefault(prof_id, []).append(c[1])#agregar nombre del curso a la lista del profesor
        for p in profesores_consulta:#recorrer filas de profesores
            prof_id, rut, nom, ape, correo = p
            prof_obj = profesor(prof_id, rut, nom, ape, correo, cursos=cursos_por_prof.get(prof_id, []))
            print(prof_obj.presentacion())#imprimir la presentacion del objeto profesor
        print("-"*34)#imprimir línea separadora
    except Exception as e:#capturar errores
        print("Error al recuperar la lista de profesores:", e)#imprimir mensaje de error

#OPCION 7 ELIMINAR PROFESOR POR ID
def borrarProfesor(db):  # OPCIÓN 7: borrar profesor y sus cursos/inscripciones
    try:
        print("\n--- Lista de Profesores ---")
        profesores = db.ejecutar_consulta("""
            SELECT id_profesor, nombre, apellido
            FROM Profesor
            ORDER BY id_profesor
        """)
        for prof in profesores:
            print(f"id: {prof[0]}, Nombre: \033[92m{prof[1]} {prof[2]}\033[0m")
        print("-"*34)

        id_a_eliminar = input("Ingrese el ID del profesor a eliminar: ").strip()
        if not id_a_eliminar.isdigit():
            print("\033[31mEl ID debe ser numérico.\033[0m")
            return
        profesor_id = int(id_a_eliminar)

        confirma = input("Esto eliminará al profesor, sus cursos y las inscripciones de esos cursos. ¿Continuar? (S/N): ").strip().upper()
        if confirma != "S":
            print("Operación cancelada.")
            return

        # 1) Borrar inscripciones de los cursos del profesor
        db.ejecutar_instruccion("""
            DELETE FROM Inscripcion
            WHERE id_curso IN (SELECT id_curso FROM Curso WHERE id_profesor = :id)
        """, {"id": profesor_id})

        # 2) Borrar cursos del profesor
        db.ejecutar_instruccion("""
            DELETE FROM Curso
            WHERE id_profesor = :id
        """, {"id": profesor_id})

        # 3) Borrar profesor
        db.ejecutar_instruccion("""
            DELETE FROM Profesor
            WHERE id_profesor = :id
        """, {"id": profesor_id})

        print("\033[92mProfesor, sus cursos e inscripciones asociadas eliminados.\033[0m")

    except Exception as e:
        print("Error al eliminar profesor y dependencias:", e)

#opcion 9 AGREGAR ESTUDIANTE A CURSO
def agregarEstudianteACurso(db):#definir función
    print("\n--- Agregar Estudiante a Curso ---")
    try:#capturar errores
        estudiantes = db.ejecutar_consulta("SELECT id_estudiante, nombre, apellido, rut FROM Estudiante ORDER BY id_estudiante")#obtener filas de estudiantes
        if not estudiantes:#si no hay estudiantes
            print("No hay estudiantes.")
            return# salir de la función
        print("Estudiantes:")
        for est in estudiantes:#recorrer filas de estudiantes
            est_obj = estudiante(est[0], est[3], est[1], est[2], None, None)  # mapa rápido para impresión
            #id, rut, nombre, apellido
            print(f"Estudiante Id: \033[31m{est_obj.id_estudiante}\033[0m, Nombre: \033[92m{est_obj.nombre} {est_obj.apellido}\033[0m, RUT: {est_obj.rut}")

        cursos = db.ejecutar_consulta("SELECT id_curso, codigo, nombre FROM Curso ORDER BY id_curso")#obtener filas de cursos
        if not cursos:#si no hay cursos
            print("No hay cursos.")
            return# salir de la función
        print("\nCursos:")
        for c in cursos:#recorrer filas de cursos
            curso_obj = curso(c[0], c[1], c[2], None, None)# mapa rápido para impresión
            #id_curso, codigo, nombre
            print(f"Curso Id: \033[31m{curso_obj.id_curso}\033[0m, Código: \033[92m{curso_obj.codigo}\033[0m, Nombre: {curso_obj.nombre}")
            #cursoid, codigo, nombre

        estudiante_a_agregar = input("\nIngrese el ID del estudiante a agregar al curso: ").strip()#input id estudiante y quitar espacios
        curso_a_agregar = input("Ingrese el ID del curso: ").strip()#input id curso y quitar espacios
        if not estudiante_a_agregar.isdigit() or not curso_a_agregar.isdigit():#validar que ambos ids sean numéricos
            print("IDs inválidos.")
            return# salir de la función
        estudiante_id = int(estudiante_a_agregar)#convertir id estudiante a entero
        curso_id = int(curso_a_agregar)#convertir id curso a entero

        existe_estudiante = [e for e in estudiantes if e[0] == estudiante_id]#verificar si el estudiante existe
        existe_curso = [c for c in cursos if c[0] == curso_id]#verificar si el curso existe
        if not existe_estudiante:#si no existe el estudiante
            print("No existe un estudiante con ese ID.")
            return# salir de la función
        if not existe_curso:#si no existe el curso
            print("No existe un curso con ese ID.")
            return# salir de la función

        ya_existe = db.ejecutar_consulta("SELECT 1 FROM Inscripcion WHERE id_estudiante = :e AND id_curso = :c", {"e": estudiante_id, "c": curso_id})
        if ya_existe:#si ya está inscrito
            print("\033[31mEl estudiante ya está inscrito en ese curso.\033[0m")
            return# salir de la función

        db.ejecutar_instruccion("INSERT INTO Inscripcion (id_inscripcion, id_estudiante, id_curso) VALUES (seq_inscripcion.NEXTVAL, :e, :c)", {"e": estudiante_id, "c": curso_id})#insertar inscripción en la base de datos
        est_consulta = existe_estudiante[0]#obtener datos del estudiante
        cur_consulta = existe_curso[0]#obtener datos del curso
         #est_consulta tiene id_estudiante, nombre, apellido, rut
        print(f"Estudiante \033[92m{est_consulta[1]} {est_consulta[2]}\033[0m agregado al curso \033[92m{cur_consulta[1]} ({cur_consulta[2]})\033[0m")#imprimir mensaje de éxito
    except Exception as e:#capturar errores
        print("Error al agregar estudiante al curso:", e)
#OPCION 10 CREAR CURSO
def crearCurso(db):#funcion crear curso
    print("\n--- Crear Curso ---")
    try:#capturar errores
        codigo = input("Código del curso (ej: MAT101): ").strip().upper()#input código y convertir a mayúsculas
        if not codigo:#validar código no vacío
            print("Código obligatorio.")
            return# salir de la función
        nombre_curso = input("Nombre del curso: ").strip()#input nombre y quitar espacios
        if not nombre_curso or len(nombre_curso) < 3:
            print("Nombre inválido.")
            return# salir de la función
        semestre = input("Semestre (formato YYYY-1 o YYYY-2): ").strip()#input semestre y quitar espacios
        if not validar_semestre(semestre):
            print("Formato de semestre inválido.")
            return# salir de la función

        profesores = db.ejecutar_consulta("SELECT id_profesor, nombre, apellido FROM Profesor ORDER BY id_profesor")#obtener filas de profesores
        if not profesores:#si no hay profesores
            print("Debe crear un profesor antes de crear cursos.")
            return
        print("Profesores disponibles:")#imprimir profesores disponibles
        for p in profesores:#recorrer filas de profesores
            print(f"Profesor Id: {p[0]}, Nombre: {p[1]} {p[2]}")#imprimir id y nombre del profesor

        profesor_id = input("Ingrese el ID del profesor responsable: ").strip()#input id profesor y quitar espacios
        if not profesor_id.isdigit():#validar que el id sea numérico
            print("ID inválido.")
            return
        profesor_id = int(profesor_id)#convertir id a entero
        existe_prof = [p for p in profesores if p[0] == profesor_id]#verificar si el profesor existe
        if not existe_prof:
            print("No existe un profesor con ese ID.")
            return

        # Insertar usando las columnas tal como están en tu SQL
        db.ejecutar_instruccion(
            "INSERT INTO Curso (id_curso, codigo, nombre, semestre, id_profesor) VALUES (seq_curso.NEXTVAL, :cod, :n, :s, :p)",
            {"cod": codigo, "n": nombre_curso.capitalize(), "s": semestre, "p": profesor_id}
        )#insertar curso en la base de datos
        print("\033[92mCurso creado correctamente.\033[0m")#imprimir mensaje de éxito
    except Exception as e:#capturar errores
        print("Error al crear el curso:", e)

#OPCION 8 CREAR PROFESOR
def crearProfesor(db):#funcion crear profesor
    print("\n--- Crear Profesor ---")
    try:#capturar errores
        rut = input("RUT (xx.xxx.xxx-x): ").strip()#input rut y quitar espacios
        if not validar_rut(rut):#validar formato de rut
            print("RUT inválido.")
            return# salir de la función
        nombre = input("Nombre: ").strip()#input nombre y quitar espacios
        if not nombre or len(nombre) < 3:#validar nombre no vacío y al menos 3 caracteres
            print("Nombre inválido.")
            return# salir de la función
        apellido = input("Apellido: ").strip()#input apellido y quitar espacios
        correo = input("Correo: ").strip()#input correo y quitar espacios
        if correo and not validar_correo(correo):#validar formato de correo si se ingresó
            print("Correo inválido.")
            return# salir de la función

        duplicado = db.ejecutar_consulta("SELECT 1 FROM Profesor WHERE rut = :rut", {"rut": rut})#verificar si ya existe un profesor con el mismo rut
        if duplicado:#si ya existe un profesor con el mismo rut
            print("\033[31mEl RUT ya existe para otro profesor.\033[0m")
            return# salir de la función

        db.ejecutar_instruccion(
            "INSERT INTO Profesor (id_profesor, rut, nombre, apellido, correo) VALUES (seq_profesor.NEXTVAL, :rut, :n, :a, :c)",
            {"rut": rut, "n": nombre.capitalize(), "a": apellido, "c": correo}
        )#insertar profesor en la base de datos
        print("\033[92mProfesor creado correctamente.\033[0m")
    except Exception as e:#capturar errores
        print("Error al crear el profesor:", e)

#OPCION 11 LISTAR CURSOS (DETALLE)
def listarCursosDetalle(db):#funcion listar cursos con detalle
    print("\n--- Lista de Cursos (Detalle) ---")
    try:#capturar errores
         # Obtener cursos con nombre del profesor
        cursos_filas = db.ejecutar_consulta("""
            SELECT c.id_curso, c.codigo, c.nombre, c.semestre, c.id_profesor, p.nombre, p.apellido
            FROM Curso c
            LEFT JOIN Profesor p ON p.id_profesor = c.id_profesor
            ORDER BY c.id_curso
        """)
        if not cursos_filas:#si no hay cursos
            print("No hay cursos registrados.")
            return# salir de la función
        cont = db.ejecutar_consulta("SELECT id_curso, COUNT(*) FROM Inscripcion GROUP BY id_curso")#obtener conteo de inscritos por curso
        inscritos = {c[0]: c[1] for c in cont}# mapa de id_curso a número de inscritos
         # Recorrer y mostrar cada curso con detalles
        for r in cursos_filas:
            # cursoid,codigo,nombre,semestre,profesorid, profnombre, profapellido=r

            cursoid, codigo, nombre, semestre, profesorid, profnombre, profapellido = r#desempaquetar fila
            curso_obj = curso(cursoid, codigo, nombre, semestre, profesorid)#crear objeto curso
            prof_nombre = f"{profnombre} {profapellido}" if profnombre else "Sin profesor"#formatear nombre del profesor
            count = inscritos.get(cursoid, 0)#obtener número de inscritos para el curso, por defecto 0
             # Imprimir detalles del curso
            print(curso_obj.presentacion(profesor_nombre=prof_nombre, inscritos=count))
    except Exception as e:#capturar errores
        print("Error al recuperar la lista de cursos:", e)

#OPCION 12 LISTAR ESTUDIANTES POR CURSO
def listarEstudiantesPorCurso(db):#funcion listar estudiantes por curso
    print("\n--- Estudiantes por Curso ---")
    try:#capturar errores
        cursos = db.ejecutar_consulta("SELECT id_curso, nombre FROM Curso ORDER BY id_curso")#obtener filas de cursos
        if not cursos:#si no hay cursos
            print("No hay cursos.")
            return# salir de la función
        for c in cursos:#recorrer filas de cursos
            print(f"Curso Id: {c[0]}, Nombre: {c[1]}")#imprimir id y nombre del curso
        id_ingresado = input("Ingrese el ID del curso: ").strip()#input id curso y quitar espacios
        if not id_ingresado.isdigit():#validar que el id sea numérico
            print("ID inválido.")
            return# salir de la función
        curso_existente = int(id_ingresado)#convertir id a entero
        existe = [c for c in cursos if c[0] == curso_existente]#verificar si el curso existe
        if not existe:#si no existe el curso
            print("Curso no encontrado.")
            return# salir de la función

        estudiantes_consulta = db.ejecutar_consulta("""
            SELECT e.id_estudiante, e.nombre, e.apellido, e.rut
            FROM Estudiante e
            JOIN Inscripcion i ON i.id_estudiante = e.id_estudiante
            WHERE i.id_curso = :c
            ORDER BY e.id_estudiante
        """, {"c": curso_existente})#obtener filas de estudiantes inscritos en el curso

        if not estudiantes_consulta:#si no hay estudiantes inscritos
            print("No hay estudiantes inscritos en este curso.")
            return

        print(f"\nEstudiantes inscritos en {existe[0][1]}:")#imprimir nombre del curso
        for e in estudiantes_consulta:#recorrer filas de estudiantes
            est_obj = estudiante(e[0], e[3], e[1], e[2], None, None)# mapa rápido para impresión
            print(f" - Id: {est_obj.id_estudiante} Nombre: {est_obj.nombre} {est_obj.apellido} RUT: {est_obj.rut}")#imprimir id, nombre, apellido y rut del estudiante
    except Exception as e:#capturar errores
        print("Error al listar estudiantes por curso:", e)