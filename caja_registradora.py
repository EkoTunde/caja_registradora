# -*- coding: utf-8 -*-

import unittest

class ItemNotFoundError(Exception):
    pass

class DineroInsuficienteError(Exception):
    pass

class ProductoNoEncontradoError(Exception):
    pass

class Producto(object):
    def __init__(self, codigo_producto:str):
        self._codigo = codigo_producto
        
    def codigo(self):
        return self._codigo
        

class ListasPrecios(object):
    def __init__(self):
        self.precios = {}
        self.descuentos = {}

    def agregar_precio_a_producto(self, producto, precio):
        self.precios[producto] = precio
    
    def agregar_descuento_a_producto(self, producto, porcentaje):
        self.descuentos[producto] = porcentaje

    def obtener_precio(self, producto):
        return self.precios[producto]
        
    def obtener_precio_con_descuento(self, producto):
        return self.precios[producto] - (self.precios[producto] * self.descuentos.get(producto, 0))
        
class Compra(object):
    def __init__(self):
        self._productos = []
    
    def productos(self):
        return self._productos

    def agregar_producto(self, producto):
        self._productos.append(producto)
    
    def quitar_producto(self, producto):
        try:
            self._productos.remove(producto)
        except ValueError:
            raise ItemNotFoundError("El producto no se agregó a la compra")

    def terminar(self):
       self._productos = []


class CajaRegistradora(object):
    def __init__(self, stock: list, lista_de_precios: ListasPrecios):
        self._stock = stock
        self._lista_de_precios = lista_de_precios
        self._compra = Compra()
        self.comprando = True

    def agregar_producto(self, codigo_producto):
        coincidencias = filter(lambda prod: prod.codigo() == codigo_producto, self._stock)
        if not coincidencias:
            raise ProductoNoEncontradoError("El producto indicado no está en la lista")
        else:
            producto = coincidencias.__next__()
            self._compra.agregar_producto(producto)
    
    def subtotal(self):
        subtotal = 0
        for producto in self._compra.productos():
            subtotal += self._lista_de_precios.obtener_precio(producto)
        return subtotal

    def compra(self):
        return self._compra

    def precios(self):
        return self._lista_de_precios

    def finalizar_compra(self):
        self.comprando = False
        self._compra.terminar()
    
    def total(self):
        total = 0
        for producto in self._compra.productos():
            total += self._lista_de_precios.obtener_precio_con_descuento(producto)
        return total

    def pagar_con(self, cantidad):
        total = self.total()
        if total > cantidad:
            raise DineroInsuficienteError("Necesita más dinero para pagar la compra")
        return cantidad - self.total()


class TestCajaRegistradora(unittest.TestCase):

    def setUp(self):
        aceite = Producto('0001')
        sal = Producto('0002')
        queso = Producto('0003')
        pan = Producto('0004')

        self.precios = ListasPrecios()
        self.precios.agregar_precio_a_producto(aceite, 25.5)
        self.precios.agregar_precio_a_producto(sal, 10.9)
        self.precios.agregar_precio_a_producto(queso, 5.25)
        self.precios.agregar_precio_a_producto(pan, 13.0)

        self.stock = [aceite, sal, queso, pan]

        self.caja = CajaRegistradora(self.stock, self.precios)

    def test_agregar_producto(self):
        self.caja.agregar_producto('0001')
        self.caja.agregar_producto('0002')
        self.caja.agregar_producto('0003')
        self.assertEqual(3, len(self.caja.compra().productos()))

    def test_subtotal_1(self):
        self.caja.agregar_producto('0001')
        self.caja.agregar_producto('0002')
        self.caja.agregar_producto('0003')
        result = self.caja.subtotal()
        self.assertEqual(41.65,result)

    def test_subtotal_2(self):
        self.caja.agregar_producto('0003')
        self.caja.agregar_producto('0004')
        result = self.caja.subtotal()
        self.assertEqual(18.25,result)

    def test_finaliza_compra(self):
        self.caja.agregar_producto('0003')
        self.caja.agregar_producto('0004')
        self.caja.finalizar_compra()
        self.assertEqual(0, len(self.caja.compra().productos()))

    def test_total_compra_con_descuento(self):
        aceite = Producto('0001')
        sal = Producto('0002')

        self.precios = ListasPrecios()
        self.precios.agregar_precio_a_producto(aceite, 75.5)
        self.precios.agregar_precio_a_producto(sal, 24.5)
        self.precios.agregar_descuento_a_producto(sal,0.5)

        self.stock = [aceite, sal]

        self.caja = CajaRegistradora(self.stock, self.precios)
        self.caja.agregar_producto('0001')
        self.caja.agregar_producto('0002')
        result = self.caja.total()
        self.assertEqual(87.75, result)

    def test_vuelto_a_cliente(self):
        self.caja.agregar_producto('0001')
        result = self.caja.pagar_con(100)
        self.assertEqual(74.5,result)



if __name__ == '__main__':
    unittest.main()

