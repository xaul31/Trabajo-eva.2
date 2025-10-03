-- Creación del usuario

CREATE USER C##evaluacion_2 IDENTIFIED BY contraseña231;
GRANT CONNECT, RESOURCE TO C##evaluacion_2 ;
ALTER USER C##evaluacion_2 QUOTA UNLIMITED ON USERS;

-- Secuencias para ID

CREATE SEQUENCE seq_estudiante START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_profesor START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_curso START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_inscripcion START WITH 1 INCREMENT BY 1;


-- TABLA: Estudiante

CREATE TABLE Estudiante (
    id_estudiante NUMBER PRIMARY KEY,
    rut VARCHAR2(15) UNIQUE NOT NULL,
    nombre VARCHAR2(100) NOT NULL,
    apellido VARCHAR2(100) NOT NULL,
    correo VARCHAR2(100) UNIQUE NOT NULL,
    fecha_nacimiento DATE
);


-- TABLA: Profesor

CREATE TABLE Profesor (
    id_profesor NUMBER PRIMARY KEY,
    rut VARCHAR2(15) UNIQUE NOT NULL,
    nombre VARCHAR2(100) NOT NULL,
    apellido VARCHAR2(100) NOT NULL,
    correo VARCHAR2(100) UNIQUE NOT NULL,
    especialidad VARCHAR2(100)
);


-- TABLA: Curso

CREATE TABLE Curso (
    id_curso NUMBER PRIMARY KEY,
    codigo VARCHAR2(10) UNIQUE NOT NULL,
    nombre VARCHAR2(100) NOT NULL,
    semestre VARCHAR2(10) NOT NULL,
    id_profesor NUMBER NOT NULL,
    CONSTRAINT fk_profesor FOREIGN KEY (id_profesor) REFERENCES Profesor(id_profesor)
);


-- TABLA: Inscripcion

CREATE TABLE Inscripcion (
    id_inscripcion NUMBER PRIMARY KEY,
    id_estudiante NUMBER NOT NULL,
    id_curso NUMBER NOT NULL,
    fecha_inscripcion DATE DEFAULT SYSDATE,
    estado VARCHAR2(20) DEFAULT 'Activa',
    CONSTRAINT fk_estudiante FOREIGN KEY (id_estudiante) REFERENCES Estudiante(id_estudiante),
    CONSTRAINT fk_curso FOREIGN KEY (id_curso) REFERENCES Curso(id_curso),
    CONSTRAINT uq_inscripcion UNIQUE (id_estudiante, id_curso)
);


-- INSTERT de prueba (Estudiantes)

INSERT INTO Estudiante (id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento)
VALUES (seq_estudiante.NEXTVAL, '11.111.111-1', 'Pedro', 'Gómez', 'pedro.gomez@correo.com', DATE '2000-01-01');

INSERT INTO Estudiante (id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento)
VALUES (seq_estudiante.NEXTVAL, '22.222.222-2', 'María', 'Pérez', 'maria.perez@correo.com', DATE '2001-05-12');

INSERT INTO Estudiante (id_estudiante, rut, nombre, apellido, correo, fecha_nacimiento)
VALUES (seq_estudiante.NEXTVAL, '33.333.333-3', 'Juan', 'Soto', 'juan.soto@correo.com', DATE '1999-11-30');


--(profesores)

INSERT INTO Profesor (id_profesor, rut, nombre, apellido, correo, especialidad)
VALUES (seq_profesor.NEXTVAL, '44.444.444-4', 'Ana', 'Martínez', 'ana.martinez@correo.com', 'Matemáticas');

INSERT INTO Profesor (id_profesor, rut, nombre, apellido, correo, especialidad)
VALUES (seq_profesor.NEXTVAL, '55.555.555-5', 'Carlos', 'López', 'carlos.lopez@correo.com', 'Computación');

--(cursos)

INSERT INTO Curso (id_curso, codigo, nombre, semestre, id_profesor)
VALUES (seq_curso.NEXTVAL, 'MAT101', 'Álgebra I', '2025-1', 1);

INSERT INTO Curso (id_curso, codigo, nombre, semestre, id_profesor)
VALUES (seq_curso.NEXTVAL, 'INF201', 'Programación I', '2025-1', 2);

INSERT INTO Curso (id_curso, codigo, nombre, semestre, id_profesor)
VALUES (seq_curso.NEXTVAL, 'INF202', 'Bases de Datos', '2025-1', 2);

--(inscripciones)

-- pedro en Álgebra I
INSERT INTO Inscripcion (id_inscripcion, id_estudiante, id_curso)
VALUES (seq_inscripcion.NEXTVAL, 1, 1);

-- maria en Programacion I
INSERT INTO Inscripcion (id_inscripcion, id_estudiante, id_curso)
VALUES (seq_inscripcion.NEXTVAL, 2, 2);

-- juan en bases de datos
INSERT INTO Inscripcion (id_inscripcion, id_estudiante, id_curso)
VALUES (seq_inscripcion.NEXTVAL, 3, 3);

-- pedro en programación I
INSERT INTO Inscripcion (id_inscripcion, id_estudiante, id_curso)
VALUES (seq_inscripcion.NEXTVAL, 1, 2);

-- maria en bases de datos
INSERT INTO Inscripcion (id_inscripcion, id_estudiante, id_curso)
VALUES (seq_inscripcion.NEXTVAL, 2, 3);

