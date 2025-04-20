from fastapi import FastAPI, HTTPException
from models import Base, Vuelo, EstadoVuelo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from TDAListaDoble import ListaVuelos
from exceptions import OwnEmpty, OwnValueError
import json
from typing import List

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
    estado: EstadoVuelo,  # Ahora define si es emergencia
    origen: str,
    destino: str
):
    db = Session()
    try:
        vuelo = Vuelo(
            codigo=codigo,
            estado=estado,  # "emergencia" activa la prioridad
            origen=origen,
            destino=destino
        )
        db.add(vuelo)
        db.commit()
        
        # Prioridad automática si el estado es "emergencia"
        if estado == EstadoVuelo.EMERGENCIA:
            lista_vuelos.insertar_al_frente(vuelo)
        else:
            lista_vuelos.insertar_al_final(vuelo)
        
        return {
            "mensaje": "Vuelo agregado",
            "vuelo": vuelo.codigo,
            "prioridad": "Alta" if estado == EstadoVuelo.EMERGENCIA else "Normal"
        }
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
    try:
        vuelo = db.query(Vuelo).filter(Vuelo.codigo == codigo).first()
        if not vuelo:
            raise HTTPException(status_code=404, detail="Vuelo no encontrado")

        # Elimina el original y lo reinserta en la nueva posición
        lista_vuelos.insertar_en_posicion(vuelo, posicion)
        db.commit()  # Solo para sincronizar relaciones (no borra de BD)

        return {
            "mensaje": f"Vuelo {codigo} movido a posición {posicion}",
            "lista_actual": [v.codigo for v in lista_vuelos.listar_vuelos()]  # Para debug
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.delete("/vuelos/extraer")
def extraer_vuelo_posicion(posicion: int):
    db = Session()
    try:
        # Extraer el vuelo de la lista
        vuelo_extraido = lista_vuelos.extraer_de_posicion(posicion)
        
        # Eliminar de la base de datos
        db.delete(vuelo_extraido)
        db.commit()
        
        return {
            "mensaje": f"Vuelo {vuelo_extraido.codigo} eliminado de la posición {posicion}",
            "vuelo_eliminado": {
                "codigo": vuelo_extraido.codigo,
                "estado": vuelo_extraido.estado.value
            }
        }
    except OwnValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        db.close()

@app.get("/vuelos/lista")
def listar_vuelos():
    return {"vuelos": [{"codigo": v.codigo, "estado": v.estado} for v in lista_vuelos.listar_vuelos()]}

@app.patch("/vuelos/reordenar")
def reordenar_vuelos(nuevo_orden: List[str]):
    """
    Reordena la lista de vuelos según los códigos proporcionados.
    Ejemplo: ["AV202", "EM001", "VL205"]
    """
    db = Session()
    try:
        # Verificar que todos los códigos existan en la BD
        vuelos_en_bd = {v.codigo: v for v in db.query(Vuelo).all()}
        vuelos_a_reordenar = []
        
        for codigo in nuevo_orden:
            if codigo not in vuelos_en_bd:
                raise HTTPException(
                    status_code=404,
                    detail=f"Vuelo {codigo} no encontrado en la BD"
                )
            vuelos_a_reordenar.append(vuelos_en_bd[codigo])
        
        # Crear una nueva lista temporal
        lista_temporal = ListaVuelos()
        
        # Reinsertar los vuelos en el nuevo orden
        for vuelo in vuelos_a_reordenar:
            lista_temporal.insertar_al_final(vuelo)
        
        # Reemplazar la lista original
        global lista_vuelos
        lista_vuelos = lista_temporal
        
        return {
            "mensaje": "Lista de vuelos reordenada",
            "nuevo_orden": [v.codigo for v in lista_vuelos.listar_vuelos()]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

