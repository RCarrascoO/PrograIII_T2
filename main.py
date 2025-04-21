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
    try:
        vuelos = db.query(Vuelo).order_by(Vuelo.hora).all()
        lista_vuelos = ListaVuelos()
        # Expulsar los objetos de la sesión pero mantener los datos
        for vuelo in vuelos:
            db.expunge(vuelo)  # Desconecta el objeto pero mantiene sus datos
            lista_vuelos.insertar_al_final(vuelo)
        return lista_vuelos
    finally:
        db.close()
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
    # Crear una lista con los datos básicos (no objetos ORM)
    vuelos = []
    for v in lista_vuelos.listar_vuelos():
        vuelos.append({
            "codigo": v.codigo,
            "estado": v.estado.value if isinstance(v.estado, EstadoVuelo) else v.estado,
            "origen": v.origen,
            "destino": v.destino
        })
    return {"vuelos": vuelos}


@app.patch("/vuelos/reordenar")
def reordenar_vuelo(codigo: str, nuevo_estado: EstadoVuelo):
    db = Session()
    try:
        # 1. Buscar el vuelo en BD con la sesión actual
        vuelo = db.query(Vuelo).filter(Vuelo.codigo == codigo).first()
        if not vuelo:
            raise HTTPException(status_code=404, detail="Vuelo no encontrado")

        # 2. Guardar estado anterior
        estado_anterior = vuelo.estado

        # 3. Actualizar el objeto completo en memoria
        vuelo.estado = nuevo_estado
        db.commit()  # Primero actualizamos la BD

        # 4. Reordenamiento físico en la lista
        if nuevo_estado != estado_anterior:
            # Eliminar el vuelo (si existe)
            elemento, pos_original = lista_vuelos._eliminar_por_id(vuelo.id)
            
            if elemento:
                # Clonar el objeto actualizado
                vuelo_actualizado = Vuelo(
                    id=vuelo.id,
                    codigo=vuelo.codigo,
                    estado=vuelo.estado,
                    origen=vuelo.origen,
                    destino=vuelo.destino,
                    hora=vuelo.hora
                )
                
                if nuevo_estado == EstadoVuelo.EMERGENCIA:
                    lista_vuelos.insertar_al_frente(vuelo_actualizado)
                elif nuevo_estado == EstadoVuelo.RETRASADO:
                    lista_vuelos.insertar_al_final(vuelo_actualizado)
                else:  # programado
                    lista_vuelos.insertar_en_posicion(vuelo_actualizado, pos_original)

        return {
            "mensaje": f"Estado actualizado a {nuevo_estado.value}",
            "en_bd": vuelo.estado.value,
            "en_lista": lista_vuelos._buscar_por_id(vuelo.id).estado.value if lista_vuelos._buscar_por_id(vuelo.id) else "no_encontrado"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
