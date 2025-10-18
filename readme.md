# 🎓 Sistema Académico de Inscripción (Python + Oracle)

Aplicación de consola en Python que permite gestionar estudiantes, profesores, cursos e inscripciones académicas conectadas a una base de datos Oracle. Incluye autenticación segura con contraseñas hasheadas y validaciones de entrada para mantener la integridad de los datos.

---

## 🧩 Características principales
- Login de administrador con verificación hash (seguro y configurable en `.env`).
- Conexión a base de datos Oracle mediante el paquete `oracledb`.
- Validaciones de formato (RUT, correo electrónico, fechas, semestre).
- Operaciones CRUD sobre estudiantes y profesores.
- Listado detallado de cursos, inscripciones y relaciones.
- Limpieza de consola y mensajes en colores para mejor experiencia visual.

---

## 🛠 Requisitos
- Python **3.7 o superior**
- **Oracle Database** (local o remoto, por ejemplo: Oracle XE)
- **Oracle Instant Client** instalado y accesible en el sistema
- Paquetes Python requeridos:

```bash
pip install oracledb python-dotenv pwinput
```

---
## Menú
1. Listar estudiantes
2. Agregar estudiante
3. Buscar estudiante por nombre (prefijo)
4. Eliminar estudiante por ID
5. Modificar edad de estudiante por ID
6. Listar profesores y sus cursos
7. Eliminar profesor (bloqueado si tiene cursos)
8. Agregar estudiante a curso (inscripción) ⚠️*en desarrollo*
9. Crear curso (con semestre y profesor)⚠️ *en desarrollo*
10. Crear profesor⚠️*en desarrollo*
11. Listar cursos (detalle, intenta mostrar semestre)⚠️*en desarrollo*
12. Listar estudiantes por curso⚠️ *en desarrollo*
13. Salir

---

## ⚙️ Archivo `.env` (ejemplo)

```env
# Configuración de conexión Oracle
DB_SERVER=localhost:1521
DB_NAME=XEPDB1
DB_USER=C##evaluacion_2
DB_PASSWORD=contrasena231

# Credenciales de administrador
ADMIN_USER=admin
ADMIN_SALT=S4LT_2025
ADMIN_PASSWORD_HASH=f6fcf397919a6e23d5892d7ec83c5276245becd194a7260cfa060999a2cf7489  # Ejemplo
```
> **Importante**
>No subir el archivo .env al repositorio (agregarlo al .gitignore)
>Cambia el valor de ADMIN_SALT y vuelve a generar el hash.
>Si usas una base de datos remota, el DB_SERVER debe incluir el host y el puerto (por ejemplo: 192.168.100.25:1521)

---

## Cómo generar el hash de la contraseña
```python
import hashlib
salt = "S4LT_2025"          # Debe coincidir con ADMIN_SALT
password = "contrasena231"  # Tu contraseña real
print(hashlib.sha256((salt + password).encode()).hexdigest())
```

Copia el resultado y reemplázalo en la variable `ADMIN_PASSWORD_HASH` del archivo `.env`.

---

## Ejecución
```bash
python main.py
```
Si el login es exitoso, se mostrará el **menú principal** con las distintas opciones de gestión.

---

## Estado del desarrollo
Algunas funciones se encuentran en desarrollo o pendientes a mejora
- `agregarEstudianteACurso`
- `crearCurso`
- `crearProfesor`
- `listarCursosDetalle`
- `listarEstudiantesPorCurso`

---

## 👤Autores:
Nelson Villagran 
Jorge Campos 
Rodrigo Hidalgo 
Vicente Mardones 
Diego Ceballos