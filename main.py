from fastapi import FastAPI, HTTPException
from models import Base, Vuelo, EstadoVuelo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from TDAListaDoble import ListaVuelos
from exceptions import OwnEmpty, OwnValueError
import json

app = FastAPI()
engine = create_engine('sqlite:///aeropuerto.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Inicializar la lista doblemente enlazada con vuelos de la BD
def cargar_vuelos_desde_bd():
    db = Session()
    vuelos = db.query(Vuelo).order_by(Vuelo.hora).all()
    lista_vuelos = ListaVuelos()
    for vuelo in vuelos:
        lista_vuelos.insertar_al_final(vuelo)
    db.close()
    return lista_vuelos

lista_vuelos = cargar_vuelos_desde_bd()

@app.post("/vuelos/")
def agregar_vuelo(
    codigo: str,
    estado: EstadoVuelo,  
    origen: str,
    destino: str,
    es_emergencia: bool = False
):
    db = Session()
    try:
        vuelo = Vuelo(
            codigo=codigo,
            estado=estado,  # Automáticamente validado
            origen=origen,
            destino=destino
        )
        db.add(vuelo)
        db.commit()
        
        if es_emergencia:
            lista_vuelos.insertar_al_frente(vuelo)
        else:
            lista_vuelos.insertar_al_final(vuelo)
        
        return {"mensaje": "Vuelo agregado", "vuelo": vuelo.codigo}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/vuelos/total")
def total_vuelos():
    return {"total": len(lista_vuelos)}

@app.get("/vuelos/proximo")
def obtener_proximo_vuelo():
    try:
        vuelo = lista_vuelos.obtener_primero()
        return {"vuelo": vuelo.codigo, "estado": vuelo.estado}
    except OwnEmpty:
        raise HTTPException(status_code=404, detail="No hay vuelos programados")
    
#Por arreglar
@app.get("/vuelos/ultimo")
def obtener_ultimo_vuelo():
    try:
        vuelo = lista_vuelos.obtener_ultimo()
        return {"vuelo": vuelo.codigo, "estado": vuelo.estado}
    except OwnEmpty:
        raise HTTPException(status_code=404, detail="No hay vuelos programados")


@app.post("/vuelos/insertar")
def insertar_vuelo_posicion(codigo: str, posicion: int):
    db = Session()
    vuelo = db.query(Vuelo).filter(Vuelo.codigo == codigo).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    
    try:
        lista_vuelos.insertar_en_posicion(vuelo, posicion)
        return {"mensaje": f"Vuelo {codigo} insertado en posición {posicion}"}
    except OwnValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/vuelos/lista")
def listar_vuelos():
    return {"vuelos": [{"codigo": v.codigo, "estado": v.estado} for v in lista_vuelos.listar_vuelos()]}