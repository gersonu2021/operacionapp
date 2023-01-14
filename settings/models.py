#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys
reload(sys)    # re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')
from collections import namedtuple
from config import *
from pprint import pprint
from flask import g

##########
# FORMAT # 
##########

#   columns: Column Name [0], Type [1], Column Display Name [2], Default Value [3]
#   foreigns: Table A [0], Column A Name [1], Table B [2], Column B Index [3], Column B Data [4], Type [5], Column Display Name [6]
#   defaults:
#     view:
#       Columnas que serán visibles por el usuario
#     edit:
#       Columnas que serán editables por el usuario
#     required:
#       Columnas obligatorios en el proceso de CRUD. No utilizar para campos booleans.
#     search:  
#       Columnas en las cuales se podrán realizar búsquedas
#     export:
#       Columnas permitidas para su exportación
#     import:
#       Columnas permitidas para su importación
#
#     Time Defaults References:
#       http://dev.mysql.com/doc/refman/5.7/en/date-and-time-functions.html
#       http://www.mysqlformatdate.com
#       SELECT DATE_FORMAT('date','%d/%m/%Y') AS showdate FROM table ORDER BY date DESC
#       ON UPDATE CURRENT_TIMESTAMP

############
# CREATION #
############

usuarios = {
  'title': 'Usuarios',
  'table': 'usuarios',
  'columns': [
    ['id', 'index', 'ID'],
    ['nombre', 'text', 'Nombre'],
    ['apellido', 'text', 'Apellido'],
    ['password', 'text', 'Password'],
    ['email', 'email', 'Email'],
    #['admin', 'boolean', 'Admin', 0],
    ['tipo', 'integer', 'Tipo'],
    # tipos: 1 Admin, 2 Maestro
    ['estado', 'boolean', 'Estado', 1],
    ['telefono', 'text', 'Teléfono'],
    ['token_password', 'text', 'Token Password'],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'defaults' : {
    'view' : ['nombre', 'apellido', 'password', 'email', 'telefono'],
    }
}

"""
ordenes_de_trabajo = {
  'title': 'Ordenes de Trabajo',
  'table': 'ordenes_de_trabajo',
  'columns': [
    ['id', 'index', 'ID'],
    ['cliente', 'integer', 'Cliente'],
    ['email', 'email', 'Email'],
    ['telefono', 'text', 'Télefono'],
    ['valor_total', 'text', 'Valor Total'],
    ['estado', 'boolean', 'Estado', 1],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'defaults' : {
    'view' : ['id', 'cliente', 'email', 'telefono', 'valor_total'],
    'edit' : ['cliente', 'email', 'telefono', 'valor_total'],
    'required' : ['cliente', 'email', 'telefono']
    }
}
"""

clientes = {
  'title': 'Clientes',
  'table': 'clientes',
  'columns': [
    ['id', 'index', 'ID'],
    ['rut', 'text', 'RUT Cliente'],
    ['direccion', 'text', 'Dirección'],
    ['razon_social', 'text', 'Nombre o Razón Social'],
    ['giro', 'text', 'Giro'],
    ['estado', 'boolean', 'Estado', 1],
    ['telefono', 'text', 'Teléfono'],
    ['observaciones', 'textarea', 'Observaciones'],
    ['email', 'email', 'Email'],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'defaults' : {
    'view' : ['razon_social', 'rut', 'direccion', 'telefono', 'email', 'observaciones', 'giro'],
    'edit' : ['razon_social', 'rut', 'direccion', 'telefono', 'email', 'giro', 'observaciones', 'estado'],
    'required' : ['rut'],
    }
}

maestros = {
  'title': 'Maestros',
  'table': 'maestros',
  'columns': [
    ['id', 'index', 'ID'],
    ['rut', 'text', 'RUT'],
    ['nombre', 'text', 'Nombre'],
    ['telefono', 'text', 'Teléfono'],
    ['estado', 'boolean', 'Estado', 1],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'defaults' : {
    'view' : ['id', 'rut', 'nombre', 'telefono'],
    'edit' : ['rut', 'nombre', 'telefono', 'estado'],
    'required' : ['rut', 'nombre'],
    }
}

inventario = {
  'title': 'Inventario',
  'table': 'inventario',
  'columns': [
    ['id', 'index', 'ID'],
    ['nombre', 'text', 'Nombre'],
    ['sku', 'text', 'SKU'],
    ['stock', 'integer', 'Stock'],
    ['cantidad_minima', 'integer', 'Cantidad Mínima'],
    ['comentarios', 'textarea', 'Comentarios'],
    ['estado', 'boolean', 'Estado', 1],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'defaults' : {
    'view' : ['nombre', 'sku', 'stock', 'cantidad_minima'],
    'edit' : ['nombre', 'sku', 'stock', 'cantidad_minima', 'comentarios'],
    'required' : ['nombre', 'sku', 'stock', 'cantidad_minima'],
    }
}

bodega_motores = {
  'title': 'Bodega Motores',
  'table': 'bodega_motores',
  'columns': [
    ['id', 'index', 'ID'],
    ['fecha_ingreso', 'date', 'Fecha Ingreso'],
    ['presupuesto', 'integer', 'Presupuesto'],
    ['motor', 'text', 'Motor'],
    ['observaciones', 'textarea', 'Observaciones'],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'defaults' : {
    'view' : ['razon_social', 'rut', 'telefono', 'email', 'fecha_ppto', 'fecha_ingreso', 'presupuesto', 'motor', 'observaciones'],
    'edit' : ['razon_social', 'rut', 'telefono', 'email', 'fecha_ppto', 'fecha_ingreso', 'presupuesto', 'motor', 'observaciones'],
    'required' : ['razon_social', 'rut', 'telefono', 'email', 'fecha_ppto', 'fecha_ingreso', 'presupuesto', 'motor'],
    },
  'indexes' : ['presupuesto']
}

ordenes_de_trabajo = {
  'title': 'Ordenes de Trabajo',
  'table': 'ordenes_de_trabajo',
  'columns': [
    ['id', 'index', 'ID'],
    ['rut_cliente', 'text', 'RUT Cliente'],
    ['valor_total', 'text', 'Valor Total'],
    ['observaciones', 'text', 'Observaciones'],
    ['marca_motor', 'text', 'Marca Motor'],
    ['estado', 'integer', 'Estado', 1],
    # Estados: 0 Pendiente de Aprobación, 1 Aprobado, 2 Rechazado, 3 Retirado y Pagado, 4 Retirado Sin Cancelar
    ['prioritario', 'boolean', 'Trabajo Prioritario', 0],
    ['espera_de_repuestos', 'text', 'A la espera de repuestos'], # Categorias de trabajos separadas por coma
    ['raw', 'text', 'Raw Values'],
    ['finalizado', 'boolean', 'Finalizado'],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'defaults' : {
    'view' : ['id', 'rut_cliente', 'valor_total', 'marca_motor', 'prioritario', 'espera_de_repuestos', 'fecha_creacion'],
    'edit' : ['rut_cliente', 'valor_total'],
    'required' : ['rut_cliente', 'valor_total'],
    },
  'foreigns': [
    ['ordenes_de_trabajo', 'rut_cliente', 'clientes', 'rut', 'rut', 'select', 'RUT Cliente'],
  ],
}

trabajos = {
  'title': 'Trabajos',
  'table': 'trabajos',
  'columns': [
    ['id', 'index', 'ID'],
    ['categoria', 'integer', 'Categoría'],
    ['nombre', 'text', 'Nombre'],
    ['valor_total', 'text', 'Valor Total'],
    ['estado', 'boolean', 'Estado', 1],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'foreigns': [
    ['trabajos', 'categoria', 'categorias_trabajos', 'id', 'nombre', 'select', 'Categoría'],
  ],
  'indexes' : ['categoria']
}

categorias_trabajos = {
  'title': 'Categorias Trabajos',
  'table': 'categorias_trabajos',
  'columns': [
    ['id', 'index', 'ID'],
    ['nombre', 'text', 'Nombre'],
    ['color', 'text', 'Color'],
    ['estado', 'boolean', 'Estado', 1],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ]
}

trabajos_orden_de_trabajo = {
  'title': 'Trabajos Orden de Trabajo',
  'table': 'trabajos_orden_de_trabajo',
  'columns': [
    ['id', 'index', 'ID'],
    ['orden_de_trabajo', 'integer', 'Orden de Trabajo'],
    ['trabajo', 'integer', 'Trabajo'],
    #['categoria', 'integer', 'Categoría Trabajo'],
    ['cantidad', 'integer', 'Cantidad'],
    ['comentario', 'text', 'Comentario'],
    ['codigo', 'integer', 'Código'],
    ['valor_neto', 'text', 'Valor Neto'],
    ['fecha_inicio', 'datetime', 'Fecha Inicio'],
    ['fecha_termino', 'datetime', 'Fecha Término'],
    ['maestro', 'integer', 'Maestro'],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'foreigns': [
    ['trabajos_orden_de_trabajo', 'trabajo', 'trabajos', 'id', 'nombre', 'select', 'Trabajo'],
    ['trabajos_orden_de_trabajo', 'categoria', 'categorias_trabajos', 'id', 'nombre', 'select', 'Categoría Trabajo'],
  ],
  'indexes' : ['orden_de_trabajo', 'trabajo']
}

asignacion_de_maestros_trabajos = {
  'title': 'Asignación de Maestros por Trabajo',
  'table': 'asignacion_de_maestros_trabajos',
  'columns': [
    ['id', 'index', 'ID'],
    ['maestro', 'integer', 'Maestro'],
    ['trabajo', 'integer', 'Trabajo'],
    ['estado', 'boolean', 'Estado', 1],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'foreigns': [
    ['asignacion_de_maestros_trabajos', 'maestro', 'maestros', 'id', 'nombre', 'select', 'Maestro'],
  ],
  'indexes' : ['maestro', 'trabajo']
}

cola_de_trabajos = {
  'title': 'Cola de Trabajos',
  'table': 'cola_de_trabajos',
  'columns': [
    ['id', 'index', 'ID'],
    ['maestro', 'integer', 'Maestro', 0],
    ['trabajo', 'integer', 'Trabajo'],
    ['trabajo_orden_de_trabajo', 'integer', 'Trabajo Orden de Trabajo'],
    ['categoria_trabajo', 'integer', 'Categoría Trabajo'],
    ['orden_de_trabajo', 'integer', 'Orden de Trabajo'],
    ['prioridad', 'integer', 'Prioridad', 0],
    ['estado', 'boolean', 'Estado', 1],
    # Estados: 
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'foreigns': [
    ['cola_de_trabajo', 'maestro', 'maestros', 'id', 'nombre', 'select', 'Maestro'],
    ['cola_de_trabajo', 'trabajo', 'trabajos', 'id', 'nombre', 'select', 'Trabajo'],
    ['cola_de_trabajo', 'trabajo_orden_de_trabajo', 'trabajos_orden_de_trabajo', 'id', 'id', 'select', 'Trabajo Orden de Trabajo']
  ],
  'indexes' : ['maestro', 'trabajo', 'trabajo_orden_de_trabajo', 'categoria_trabajo', 'orden_de_trabajo', 'prioridad']
}

repuestos = {
  'title': 'Repuestos',
  'table': 'repuestos',
  'columns': [
    ['id', 'index', 'ID'],
    ['nombre', 'text', 'Nombre'],
    ['estado', 'boolean', 'Estado', 1],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ]
}

repuestos_orden_de_trabajo = {
  'title': 'Repuestos Orden de Trabajo',
  'table': 'repuestos_orden_de_trabajo',
  'columns': [
    ['id', 'index', 'ID'],
    ['repuesto', 'integer', 'Repuesto'],
    ['comentario', 'text', 'Comentario'],
    ['codigo', 'integer', 'Código'],
    ['sobre_medida', 'text', 'Sobre Medida'],
    ['cantidad', 'integer', 'Cantidad'],
    ['recibido', 'boolean', 'Recibido'],
    ['valor_neto', 'text', 'Valor Neto'],
    ['orden_de_trabajo', 'integer', 'Orden de Trabajo'],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'indexes' : ['repuesto', 'orden_de_trabajo']
}

marcas_motores = {
  'title': 'Marcas Motores',
  'table': 'marcas_motores',
  'columns': [
    ['id', 'index', 'ID'],
    ['nombre', 'text', 'Nombre'],
    ['estado', 'boolean', 'Estado', 1],
    ['fecha_creacion', 'date', 'Fecha Creación', "CURRENT_TIMESTAMP"]
  ],
  'defaults' : {
    'view' : ['nombre'],
    'edit' : ['nombre'],
    'required' : ['nombre'],
    },
}

#######################
# MODELS REGISTRATION #
#######################

models = {
  'usuarios' : usuarios,
  'ordenes_de_trabajo' : ordenes_de_trabajo,
  'clientes' : clientes,
  'maestros' : maestros,
  'inventario' : inventario,
  'bodega_motores' : bodega_motores,
  'ordenes_de_trabajo' : ordenes_de_trabajo,
  'trabajos' : trabajos,
  'categorias_trabajos' : categorias_trabajos,
  'trabajos_orden_de_trabajo' : trabajos_orden_de_trabajo,
  'asignacion_de_maestros_trabajos' : asignacion_de_maestros_trabajos,
  'repuestos' : repuestos,
  'repuestos_orden_de_trabajo' : repuestos_orden_de_trabajo,
  'cola_de_trabajos' : cola_de_trabajos,
  'marcas_motores' : marcas_motores
}
