# ISLI – Sistema de Inspección de Lotes Industriales

## 📚 Índice

1. [📖 Introducción](#1-📖-introducción)  
2. [⚙️ Instalación y Requisitos](#2-⚙️-instalación-y-requisitos)  
3. [🔐 Pantalla de Inicio de Sesión](#3-🔐-pantalla-de-inicio-de-sesión)  
   - [3.1 🔁 Recuperación de contraseña](#31-🔁-recuperación-de-contraseña)  
4. [🏠 Menú Principal – Control de Calidad](#4-🏠-menú-principal--control-de-calidad)  
   - [4.1 🧪 Ejecución paso a paso del control de calidad](#41-🧪-ejecución-paso-a-paso-del-control-de-calidad)  
   - [4.2 💾 Guardado de resultados](#42-💾-guardado-de-resultados)  
   - [4.3 🧾 Generación de informes PDF](#43-🧾-generación-de-informes-pdf)  
5. [📊 Histórico de Controles](#5-📊-histórico-de-controles)  
   - [5.1 🧮 Filtrado por usuario, fecha y tolerancia](#51-🧮-filtrado-por-usuario-fecha-y-tolerancia)  
   - [5.2 ✏️ Edición de comentarios](#52-✏️-edición-de-comentarios)  
   - [5.3 🔍 Visualización o generación de informes](#53-🔍-visualización-o-generación-de-informes)  
6. [❓ Preguntas Frecuentes (FAQ)](#6-❓-preguntas-frecuentes-faq)  
7. [🎛️ Panel Lateral de Navegación](#7-🎛️-panel-lateral-de-navegación)  
   - [7.1 👤 Visualización del usuario actual](#71-👤-visualización-del-usuario-actual)  
   - [7.2 🔄 Navegación entre ventanas](#72-🔄-navegación-entre-ventanas)  
   - [7.3 🛠️ Acceso al Panel de Administración (solo administradores)](#73-🛠️-acceso-al-panel-de-administración-solo-administradores)  
   - [7.4 🗂️ Gestor de rutas de almacén (solo administradores)](#74-🗂️-gestor-de-rutas-de-almacén-solo-administradores)  
   - [7.5 📘 Acceso al Manual de Usuario](#75-📘-acceso-al-manual-de-usuario)  
   - [7.6 🚪 Cierre de sesión](#76-🚪-cierre-de-sesión)  
8. [👤 Créditos y Mantenimiento](#8-👤-créditos-y-mantenimiento)



## 1. 📖 Introducción

...

## 2. ⚙️ Instalación y Requisitos

...

## 3. 🔐 Pantalla de Inicio de Sesión

### 3.1 🔁 Recuperación de contraseña

...

## 4. 🏠 Menú Principal – Control de Calidad

### 4.1 🧪 Ejecución paso a paso del control de calidad
### 4.2 💾 Guardado de resultados
### 4.3 🧾 Generación de informes PDF

...

## 5. 📊 Histórico de Controles

### 5.1 🧮 Filtrado por usuario, fecha y tolerancia
### 5.2 ✏️ Edición de comentarios
### 5.3 🔍 Visualización o generación de informes

...

## 6. ❓ Preguntas Frecuentes (FAQ)

...

## 7. 🎛️ Panel Lateral de Navegación

### 7.1 👤 Visualización del usuario actual
### 7.2 🔄 Navegación entre ventanas
### 7.3 🛠️ Acceso al Panel de Administración (solo administradores)
### 7.4 🗂️ Gestor de rutas de almacén (solo administradores)
### 7.5 📘 Acceso al Manual de Usuario
### 7.6 🚪 Cierre de sesión

...

## 8. 👤 Créditos y Mantenimiento



**ISLI** es una aplicación de escritorio desarrollada en **Python** con **PySide6 (Qt for Python)** que simula un sistema de visión artificial para realizar el control de calidad visual de superficies planas en diferentes industrias (plásticos, maderas, textiles, entre otros ) mediante análisis de imágenes. El sistema incluye una interfaz gráfica de usuario (GUI), un backend REST desarrollado con **FastAPI** y una base de datos **MySQL**.

Este proyecto ha sido desarrollado por **Paco Gago** como parte del **Proyecto Final del Ciclo Formativo de Grado Superior en Desarrollo de Aplicaciones Multiplataforma (CFGS DAM)**.

---

## ✨ Funcionalidades implementadas

- ✅ Inicio de sesión con autenticación de usuarios
- ✅ Visualización de imágenes con visor dual en alta calidad
- ✅ Análisis automático de imágenes por lotes
- ✅ Clasificación de defectos basada en umbrales personalizables
- ✅ Lectura y visualización de bounding boxes desde archivos `.json`
- ✅ Almacenamiento de resultados en base de datos MySQL
- ✅ Histórico de inspecciones accesible desde la interfaz
- ✅ Gestión de IDs automáticos (formato `00001`, `00002`, etc.)
- ✅ Control de sesión con logout y cambio de usuario

---

## 🧰 Tecnologías utilizadas

| Componente   | Tecnología           |
|--------------|----------------------|
| **Frontend** | PySide6 (Qt for Python) |
| **Backend**  | FastAPI              |
| **Base de datos** | MySQL           |
| **ORM**      | Conexión directa con `mysql-connector-python` |
| **Estilo visual** | Qt Designer + layouts personalizados |

---

## 📁 Estructura del repositorio

isli/
│
├── backend/
│ ├── main.py # Servidor FastAPI
│ ├── db.py # Conexión MySQL
│ ├── routers/ # Endpoints de login y controles
│ ├── schemas/ # Esquemas Pydantic
│ └── utils.py, seed_users.py, etc.
│
├── frontend/
│ ├── main.py # Lanza la ventana de login
│ ├── parpadeo.py # Ventana principal con navegación
│ └── UI/ # Archivos .ui y módulos QtDesigner
│
├── requirements.txt
├── .gitignore
└── README.md

---

## 🚀 Cómo ejecutar el proyecto

### 🔹 Backend (FastAPI)

1. Abre una terminal y entra en la carpeta `backend/`
2. Ejecuta el servidor:

```bash
uvicorn main:app --reload
Esto levantará la API REST en http://127.0.0.1:8000

🔹 Frontend (PySide6)
Abre otra terminal en la carpeta frontend/

Ejecuta la interfaz:

```bash
python main.py

👨‍💻 Autor
Francisco Muñoz
Proyecto Final – CFGS Desarrollo de Aplicaciones Multiplataforma
Tupl | 2025