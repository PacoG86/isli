# ISLI – Sistema de Inspección de Lotes Industriales

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