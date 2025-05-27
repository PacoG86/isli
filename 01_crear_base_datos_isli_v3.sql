-- Reiniciar la base de datos
DROP DATABASE IF EXISTS isli_db;
CREATE DATABASE isli_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE isli_db;

-- Tabla de usuarios
CREATE TABLE USUARIO (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(100) NOT NULL,
    email_usuario VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    rol ENUM('operario', 'administrador') NOT NULL,
    activo BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de controles de calidad
CREATE TABLE CONTROL_CALIDAD (
    id_control INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    umbral_tamano_defecto DECIMAL(5,2) NOT NULL,
    num_defectos_tolerables_por_tamano INT NOT NULL,
    fecha_control DATETIME NOT NULL,
    observacs TEXT,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de rollos inspeccionados
CREATE TABLE ROLLO (
    id_rollo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rollo VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL UNIQUE,
    ruta_local_rollo VARCHAR(255) NOT NULL,
    num_defectos_rollo INT NOT NULL,
    estado_rollo ENUM('disponible', 'controlado') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de resultados de control por rollo
CREATE TABLE ROLLO_CONTROLADO (
    id_rollo INT,
    id_control INT,
    total_defectos_intolerables_rollo INT NOT NULL,
    resultado_rollo ENUM('ok','nok') NOT NULL,
    orden_analisis INT NOT NULL CHECK (orden_analisis > 0),
    PRIMARY KEY (id_rollo, id_control),
    FOREIGN KEY (id_rollo) REFERENCES ROLLO(id_rollo) ON DELETE CASCADE,
    FOREIGN KEY (id_control) REFERENCES CONTROL_CALIDAD(id_control) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de imágenes con defecto
CREATE TABLE IMG_DEFECTO (
    id_imagen INT AUTO_INCREMENT PRIMARY KEY,
    id_rollo INT NOT NULL,
    id_control INT NOT NULL,
    nombre_archivo VARCHAR(100) NOT NULL,
    fecha_captura DATETIME NOT NULL,
    max_dim_defecto_medido DECIMAL(6,2) NOT NULL CHECK (max_dim_defecto_medido >= 0),
    clasificacion ENUM('ok','nok') NOT NULL,
    FOREIGN KEY (id_control) REFERENCES CONTROL_CALIDAD(id_control) ON DELETE CASCADE,
    FOREIGN KEY (id_rollo) REFERENCES ROLLO(id_rollo) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de defectos medidos manualmente
CREATE TABLE DEFECTO_MEDIDO (
    id_medicion INT AUTO_INCREMENT PRIMARY KEY,
    id_imagen INT NOT NULL,
    area_mm DECIMAL(6,2) NOT NULL CHECK (area_mm >= 0),
    tipo_valor ENUM('min', 'max') NOT NULL,
    tipo_defecto VARCHAR(50),  -- 'punto-negro', 'pegote-cascarilla', etc.
    FOREIGN KEY (id_imagen) REFERENCES IMG_DEFECTO(id_imagen) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de informes generados
CREATE TABLE INFORME_CONTROL (
    id_informe INT AUTO_INCREMENT PRIMARY KEY,
    id_control INT NOT NULL,
    ruta_pdf VARCHAR(255) NOT NULL,
    generado_por INT NOT NULL,
    fecha_generacion DATETIME NOT NULL,
    notas TEXT,
    FOREIGN KEY (id_control) REFERENCES CONTROL_CALIDAD(id_control) ON DELETE CASCADE,
    FOREIGN KEY (generado_por) REFERENCES USUARIO(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE SOLICITUD_CAMBIO_PASSWORD (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    email_usuario VARCHAR(100) NOT NULL,
    motivo TEXT,
    password_nueva VARCHAR(100) NOT NULL,
    estado_solicitud ENUM('pendiente', 'atendida') NOT NULL DEFAULT 'pendiente',
    timestamp TEXT NOT NULL,
    FOREIGN KEY (email_usuario) REFERENCES USUARIO(email_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

