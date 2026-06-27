# Challenge Técnico — API de Empleados
Crear una API para gestión de empleados desarrollada con Python, Flask y MongoDB.

## Requisitos previos

- Python 3.10.9 o superior instalado
- Una cuenta en [MongoDB Atlas](https://www.mongodb.com/atlas) con un cluster creado

---

## Instalación y configuración

**1. Clonar el repositorio:**
```bash
git clone https://github.com/FedericoIseas/ch-tecnico-leafnoise-BE.git
cd ch-tecnico-leafnoise-BE
```

**2. Crear y activar el entorno virtual:**
```bash
python -m venv venv_challenge_Iseas

# Windows
venv_challenge_Iseas\Scripts\activate

# Mac/Linux
source venv_challenge_Iseas/bin/activate
```

**3. Instalar las dependencias:**
```bash
pip install -r requirements.txt
```

**4. Crear el archivo `.env` en la raíz del proyecto con las siguientes variables:**
```env
MONGODB_URI=URI_de_Conexión_a_tu_cluster_de_MongoDB
DB_NAME=Nombre_de_tu_base_de_datos
JWT_SECRET=una_clave_secreta_larga_y_dificil
```

**5. Correr el servidor:**
```bash
python app.py
```

El servidor queda disponible en `http://localhost:5000`

---

## Endpoints disponibles

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/login` | Iniciar sesión y obtener token JWT |

### Empleados (requieren token JWT)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/empleados` | Listar empleados (posibilidad de filtrar por puesto y paginación) |
| GET | `/empleados/<id>` | Obtener un empleado por ID |
| POST | `/empleados` | Crear un empleado |
| PUT | `/empleados/<id>` | Actualizar un empleado |
| DELETE | `/empleados/<id>` | Eliminar un empleado |
| GET | `/empleados/estadisticas/promediosalarial` | Promedio salarial de todos los empleados |

---

## Autenticación

La API usa **JWT (JSON Web Tokens)**. Para acceder a los endpoints protegidos:

**1.** Hacé POST a `/login` con:
```json
{
    "email": "admin@mail.com",
    "password": "1234"
}
```

**2.** Copiá el token de la respuesta y envialo en el header de cada request:
```
Authorization: Bearer <tu_token>
```

---

## Parámetros de paginación y filtros

El endpoint `GET /empleados` acepta los siguientes query params:

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `puesto` | string | — | Filtra por puesto |
| `pagina` | int | 1 | Número de página |
| `limite` | int | 10 | Resultados por página |

Ejemplo:
```
GET /empleados?puesto=developer&pagina=1&limite=5
```