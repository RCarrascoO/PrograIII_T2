from TDA_Double_Linked_List import _DoublyLinkedBase
from exceptions import OwnEmpty, OwnValueError

class ListaVuelos(_DoublyLinkedBase):
    """Lista doblemente enlazada especializada para gestión de vuelos."""
    
    def insertar_al_frente(self, vuelo):
        """Añade un vuelo al inicio (emergencias)."""
        self.add_first(vuelo)
    
    def insertar_al_final(self, vuelo):
        """Añade un vuelo al final (vuelos regulares)."""
        self.add_last(vuelo)
    
    def obtener_primero(self):
        """Retorna el primer vuelo sin removerlo."""
        if self.is_empty():
            raise OwnEmpty("No hay vuelos en la lista")
        return self._header._next._element
    
    def obtener_ultimo(self):
        """Retorna el último vuelo sin removerlo."""
        if self.is_empty():
            raise OwnEmpty("No hay vuelos en la lista")
        return self._trailer._prev._element
    
    def insertar_en_posicion(self, vuelo, posicion):
        """Inserta un vuelo en una posición específica."""
        if posicion < 0 or posicion > self._size:
            raise OwnValueError("Posición inválida")
        
        if posicion == 0:
            return self.add_first(vuelo)
        elif posicion == self._size:
            return self.add_last(vuelo)
        
        current = self._header._next
        for _ in range(posicion):
            current = current._next
        self._insert_between(vuelo, current._prev, current)
    
    def extraer_de_posicion(self, posicion):
        """Elimina y retorna el vuelo en la posición dada."""
        if posicion < 0 or posicion >= self._size:
            raise OwnValueError("Posición inválida")
        
        current = self._header._next
        for _ in range(posicion):
            current = current._next
        return self._delete_node(current)
    
    def listar_vuelos(self):
        """Retorna todos los vuelos en orden."""
        vuelos = []
        current = self._header._next
        while current != self._trailer:
            vuelos.append(current._element)
            current = current._next
        return vuelos