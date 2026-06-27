from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from bson import ObjectId
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

app = Flask(__name__)

#configuración autenticación JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # expira en 1 hora (en segundos)
jwt = JWTManager(app)

#configuración conexión a MongoDB
client = MongoClient(os.getenv("MONGODB_URI")) #conecto a DB según variable de entorno
db = client[os.getenv("DB_NAME")]
coleccion_empleados = db["empleados"]

def serializar(empleado): #convertir ObjectId a string para que sea serializable a JSON
    empleado["_id"] = str(empleado["_id"])
    return empleado

def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

@app.route("/empleados", methods=["POST"]) #Crear registro
@jwt_required()
def crear_empleado():
    datos = request.get_json()
    if not datos or "nombre" not in datos or "apellido" not in datos or "email" not in datos or "puesto" not in datos or "salario" not in datos:
        return jsonify({"error": "Faltan campos requeridos. Debe enviar nombre, apellido, email, puesto y salario del nuevo empleado"}), 400
    
    if not isinstance(datos["salario"], (int, float)):
        return jsonify({"error": "El salario debe ser un número"}), 400

    if not all(isinstance(datos[campo], str) for campo in ["nombre", "apellido", "email", "puesto"]):
        return jsonify({"error": "nombre, apellido, email y puesto deben ser texto"}), 400
    
    if "fecha_ingreso" in datos and not validar_fecha(datos["fecha_ingreso"]):
        return jsonify({"error": "La fecha de ingreso debe estar en formato dd/mm/yyyy"}), 400

    nuevo_empleado = {
        "nombre": datos["nombre"],
        "apellido": datos["apellido"],
        "email": datos["email"],
        "puesto": datos["puesto"],
        "salario": datos["salario"],
        "fecha_ingreso": datos.get("fecha_ingreso", datetime.now().isoformat()),
        "fecha_creacion": datetime.now().isoformat(),
        "fecha_actualizacion": datetime.now().isoformat()
    }

    resultado = coleccion_empleados.insert_one(nuevo_empleado)
    nuevo_empleado["_id"] = str(resultado.inserted_id)
    return jsonify(nuevo_empleado), 201

@app.route("/empleados", methods=["GET"]) #obtener todos los registro con posibilidad de filtrar por puesto
@jwt_required()
def obtener_empleados():
    filtro = {}
    puesto = request.args.get("puesto")
    if puesto:
        filtro["puesto"] = puesto
    
    pagina = request.args.get("pagina", 1, type=int)
    limite = request.args.get("limite", 10, type=int)
    skip = (pagina - 1) * limite

    lista_empleados = [serializar(empleado) for empleado in coleccion_empleados.find(filtro).skip(skip).limit(limite)]
    return jsonify({
        "pagina" : pagina,
        "limite" : limite,
        "total_empleados" : coleccion_empleados.count_documents(filtro),
        "empleados" : lista_empleados
        }), 200

@app.route("/empleados/<id>", methods=["GET"]) #obtener un registro por ID
@jwt_required()
def obtener_empleado(id):
    empleado = coleccion_empleados.find_one({"_id": ObjectId(id)})
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404
    return jsonify(serializar(empleado)), 200

@app.route("/empleados/<id>", methods=["PUT"]) #actualizar un registro por ID
@jwt_required()
def actualizar_empleado(id):
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

    if "salario" in datos and not isinstance(datos["salario"], (int, float)):
        return jsonify({"error": "El salario debe ser un número"}), 400

    if any(campo in datos for campo in ["nombre", "apellido", "email", "puesto"]):
        if not all(isinstance(datos[campo], str) for campo in ["nombre", "apellido", "email", "puesto"] if campo in datos):
            return jsonify({"error": "nombre, apellido, email y puesto deben ser texto"}), 400
        
    if "fecha_ingreso" in datos and not validar_fecha(datos["fecha_ingreso"]):
        return jsonify({"error": "Formato de fecha inválido. Use DD/MM/YYYY"}), 400

    resultado = coleccion_empleados.update_one(
        {"_id": ObjectId(id)}, 
        {"$set": {**datos, "fecha_actualizacion": datetime.now().isoformat()}}
        )
    if resultado.matched_count == 0:
        return jsonify({"error": "Empleado no encontrado"}), 404
    empleado_actualizado = coleccion_empleados.find_one({"_id": ObjectId(id)})
    return jsonify(serializar(empleado_actualizado)), 200

@app.route("/empleados/<id>", methods=["DELETE"]) #eliminar un registro por ID
@jwt_required()
def eliminar_empleado(id):
    resultado = coleccion_empleados.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count == 0:
        return jsonify({"error": "Empleado no encontrado"}), 404
    return jsonify({"mensaje": "Empleado eliminado correctamente"}), 200

@app.route("/empleados/estadisticas/promediosalarial", methods=["GET"]) #obtener promedio salarial de todos los empleados
@jwt_required()
def obtener_promedio_salarial():
    total_empleados = coleccion_empleados.count_documents({})
    if total_empleados == 0:
        return jsonify({"mensaje": "No hay empleados registrados"}), 200

    pipeline = [
        {"$group": {"_id": None, "promedio_salarial": {"$avg": "$salario"}}}
    ]
    resultado = list(coleccion_empleados.aggregate(pipeline))
    if not resultado:
        return jsonify({"promedio_salarial": 0}), 200
    return jsonify(
        {
            "total_empleados": total_empleados,
            "promedio_salarial": resultado[0]["promedio_salarial"]
        }), 200

@app.route("/login", methods=["POST"]) #login para obtener token JWT
def login():
    datos = request.get_json()
    if not datos or "email" not in datos or "password" not in datos:
        return jsonify({"error": "Email y password son requeridos"}), 400
    
    #Validación de credenciales simple. Se debería verificar contra una base de datos y el password debe estar hasheado
    if datos["email"] == "admin@mail.com" and datos["password"] == "1234":
        token = create_access_token(identity=datos["email"])
        return jsonify({"token": token}), 200
    
    return jsonify({"error": "Credenciales inválidas"}), 401

if __name__ == "__main__":
    app.run(debug=True)