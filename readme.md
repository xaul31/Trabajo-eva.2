## Sistema de Inscripcion (Caso 4)
Aplicación de consola en Python para gestionar estudiantes, profesores, cursos e inscripciones sobre SQL Server. Incluye autenticación segura con contraseña hasheada y validaciones para mantener la integridad de los datos

## 🛠 Requisitos
- Python 3.7+
- SQL Server (local o remoto)
- Controlador ODBC Driver 17 for SQL Server instalado
- Paquetes Python:
```bash
pip install dotenv oracledb pwinput
```


> Importante no subir el .env al repo 

## Menú
1. Listar estudiantes
2. Agregar estudiante
3. Buscar estudiante por nombre (prefijo)
4. Eliminar estudiante por ID
5. Modificar edad de estudiante por ID
6. Listar profesores y sus cursos
7. Eliminar profesor (bloqueado si tiene cursos)
8. Agregar estudiante a curso (inscripción)
9. Crear curso (con semestre y profesor)
10. Crear profesor
11. Listar cursos (detalle, intenta mostrar semestre)
12. Listar estudiantes por curso
13. Salir



## Archivo .env Ejemplo
```env
DB_SERVER=localhost:1521
DB_NAME=xe
DB_USER=c##evaluacion_2
DB_PASSWORD=contraseña231

ADMIN_USER=admin
ADMIN_SALT=S4LT_2025
ADMIN_PASSWORD_HASH=f6fcf397919a6e23d5892d7ec83c5276245becd194a7260cfa060999a2cf7489  # Ejemplo
```
>Importante no subir el .env al repo (puedes agregarlo al git ignore), Cambiar la SAL y vuelve a generar el hash 

## 👤Autores:
Nelson Villagran, Jorge Campos, Rodrigo Hidalgo, Vicente Mardones, Diego Ceballos