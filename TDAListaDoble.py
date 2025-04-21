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
        """Elimina el vuelo original (si existe) y lo inserta en la nueva posición."""
        if posicion < 0 or posicion > self._size:
            raise OwnValueError("Posición inválida")

        # Buscar y eliminar el vuelo si ya está en la lista
        self._eliminar_por_id(vuelo.id)  # Nueva función auxiliar

        # Insertar en la nueva posición
        if posicion == 0:
            self.add_first(vuelo)
        elif posicion == self._size:
            self.add_last(vuelo)
        else:
            current = self._header._next
            for _ in range(posicion):
                current = current._next
            self._insert_between(vuelo, current._prev, current)

    def _buscar_por_id(self, id_vuelo):
        """Busca un vuelo por ID y devuelve el nodo completo"""
        current = self._header._next
        while current != self._trailer:
            if current._element.id == id_vuelo:
                return current._element
            current = current._next
        return None

    def _eliminar_por_id(self, id_vuelo):
        """Devuelve (elemento, posición_original)"""
        current = self._header._next
        pos = 0
        while current != self._trailer:
            if current._element.id == id_vuelo:
                elemento = current._element
                self._delete_node(current)
                return elemento, pos
            current = current._next
            pos += 1
        return None, -1

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
    



