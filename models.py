from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()

class EstadoVuelo(PyEnum):
    PROGRAMADO = "programado"
    EMERGENCIA = "emergencia"
    RETRASADO = "retrasado"

Base = declarative_base()

class Vuelo(Base):
    __tablename__ = 'vuelos'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), unique=True, nullable=False)
    estado = Column(Enum(EstadoVuelo), nullable=False)  # Usamos el Enum aquí
    hora = Column(DateTime, default=datetime.utcnow)
    origen = Column(String(50))
    destino = Column(String(50))
    
    def __repr__(self):
        return f"Vuelo(codigo={self.codigo}, estado={self.estado.value})"