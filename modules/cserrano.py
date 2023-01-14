#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
import sys
from settings import models
from settings.config import *
from modules.validate import Validate
from decimal import Decimal

from pprint import pprint

class Cserrano:

  def __init__(self):
    return

  def actualizar_cola(self, id_ot):
    try:
      ot = g.db.read(
        "SELECT id, estado, espera_de_repuestos, prioritario FROM ordenes_de_trabajo "
        "WHERE id = ? "
        , [ id_ot ] 
      )

      if not ot:
        g.db.mod(
          "DELETE FROM cola_de_trabajos "
          "WHERE orden_de_trabajo = ? AND NOT maestro ",
          [ int(id_ot)  ]
        )
        g.db.mod(
          "UPDATE trabajos_orden_de_trabajo "
          "SET fecha_inicio = NULL, fecha_termino = NULL, maestro = NULL "
          "WHERE orden_de_trabajo = ? "
          ,[ int(id_ot)  ]
        )
        return False

      # Pendiente de Aprobación
      if ot[0]['estado'] == 0:
        # No se muestra en la cola de trabajos y los trabajos pueden ser editados. 
        g.db.mod(
          "DELETE FROM cola_de_trabajos "
          "WHERE orden_de_trabajo = ? ",
          [ int(id_ot)  ]
        )
        return False
      # Aprobado
      if ot[0]['estado'] == 1:
        # En este estado la OT ingresará a la cola de trabajos con todos sus datos de inicio y término en blanco,
        # por lo que se al guardarla en este estado se borrarán datos antiguos si es que existieran.
        g.db.mod(
          "DELETE FROM cola_de_trabajos "
          "WHERE orden_de_trabajo = ? ",
          [ int(id_ot)  ]
        )
        #g.db.mod(
        #  "UPDATE trabajos_orden_de_trabajo "
        #  "SET fecha_inicio = NULL, fecha_termino = NULL, maestro = NULL "
        #  "WHERE orden_de_trabajo = ? "
        #  ,[ int(id_ot)  ]
        #)
      # Rechazado
      elif ot[0]['estado'] == 2:
        # Se guarda con los trabajos en el estado en que se encuentren y los trabajos no pueden ser modificados.
        g.db.mod(
          "DELETE FROM cola_de_trabajos "
          "WHERE orden_de_trabajo = ? ",
          [ int(id_ot)  ]
        )
        return False
      # Retirado y Pagado
      elif ot[0]['estado'] == 3:
        # Se guarda con los trabajos en el estado en que se encuentren y los trabajos no pueden ser modificados.
        g.db.mod(
          "DELETE FROM cola_de_trabajos "
          "WHERE orden_de_trabajo = ? ",
          [ int(id_ot)  ]
        )
        return False
      # Retirado sin Cancelar
      elif ot[0]['estado'] == 4:
        # Se guarda con los trabajos en el estado en que se encuentren y los trabajos no pueden ser modificados.
        g.db.mod(
          "DELETE FROM cola_de_trabajos "
          "WHERE orden_de_trabajo = ? ",
          [ int(id_ot)  ]
        )
        return False
      else:
        return False

      espera_de_repuestos = str(ot[0]['espera_de_repuestos'])
      query = "SELECT trabajos_orden_de_trabajo.*, "
      query += "ordenes_de_trabajo.id AS orden_de_trabajo, ordenes_de_trabajo.prioritario, "
      query += "trabajos.* "
      query += "FROM trabajos_orden_de_trabajo "
      query += "LEFT JOIN ordenes_de_trabajo "
      query += "ON trabajos_orden_de_trabajo.orden_de_trabajo = ordenes_de_trabajo.id "
      query += "LEFT JOIN trabajos "
      query += "ON trabajos_orden_de_trabajo.trabajo = trabajos.id "
      query += "WHERE ordenes_de_trabajo.id = ? "
      if espera_de_repuestos:
        query += "AND trabajos.categoria NOT IN (" + espera_de_repuestos + ") "
      query += "AND ordenes_de_trabajo.finalizado IS NULL "
      query += "AND trabajos_orden_de_trabajo.fecha_termino IS NULL "
      trabajos = g.db.read( query, [ int(id_ot) ] )

      if not trabajos:
        print ('No hay trabajos disponibles para la OT seleccionada')
        g.db.mod(
          "DELETE FROM cola_de_trabajos "
          "WHERE orden_de_trabajo = ? AND NOT maestro ",
          [ int(id_ot)  ]
        )
        g.db.mod(
          "UPDATE trabajos_orden_de_trabajo "
          "SET fecha_inicio = NULL, fecha_termino = NULL, maestro = NULL "
          "WHERE orden_de_trabajo = ? "
          ,[ int(id_ot)  ]
        )
        return False

      cola_de_trabajos = g.db.read(
        "SELECT id FROM cola_de_trabajos "
        "WHERE orden_de_trabajo = ? LIMIT 1 "
        , [ int(id_ot) ] 
      )

      # Actualiza Trabajos en Cola
      # Si el estado de la OT no es aprobado, eliminia todos los trabajos de la cola pertenecientes a esa OT y la información de los maestros asociados.
      if ot[0]['estado'] != 1:
        g.db.mod(
          "DELETE FROM cola_de_trabajos "
          "WHERE orden_de_trabajo = ? ",
          [ int(id_ot)  ]
        )
        g.db.mod(
          "UPDATE trabajos_orden_de_trabajo "
          "SET fecha_inicio = NULL, fecha_termino = NULL, maestro = NULL "
          "WHERE orden_de_trabajo = ? ",
          [ int(id_ot)  ]
        )
      # Elimina de la cola todos los trabajos que no tengan repuestos 
      if espera_de_repuestos:
        g.db.mod(
          "DELETE FROM cola_de_trabajos "
          "WHERE orden_de_trabajo = ? "
          "AND categoria_trabajo IN (" + espera_de_repuestos + ") ", 
          [ id_ot ]
        )

        ids_trabajos = g.db.read("SELECT GROUP_CONCAT(DISTINCT id SEPARATOR ',') AS ids FROM trabajos "
          "WHERE id IN (SELECT id FROM trabajos_orden_de_trabajo WHERE orden_de_trabajo = ?)"
          "AND categoria IN(" + espera_de_repuestos + ") "
          ,[ int(id_ot)  ]
        )

        #if ids_trabajos[0]['ids']:
        #  g.db.mod(
        #    "UPDATE trabajos_orden_de_trabajo "
        #    "SET fecha_inicio = NULL, fecha_termino = NULL, maestro = NULL "
        #    "WHERE orden_de_trabajo = ? "
        #    "AND trabajo IN (" + str(ids_trabajos[0]['ids']) + ") ", 
        #    [ int(id_ot)  ]
        #  )

      # Actualiza la prioridad de todos los trabajos de la OT en la cola de trabajos
      if ot[0]['prioritario'] == 1:
        g.db.mod(
          "UPDATE cola_de_trabajos SET prioridad = 1 "
          "WHERE orden_de_trabajo = ? ",
          [ int(id_ot)  ]
        )

      # Agrega Nuevos Trabajos a la Cola
      if not cola_de_trabajos:
        insert_data = []
        for row in trabajos:
          insert_data.append([row['trabajos.id'], row['id'], row['categoria'], 
            row['orden_de_trabajo'], row['prioritario'] ])
        g.db.mod(
          "INSERT INTO cola_de_trabajos "
          "(trabajo, trabajo_orden_de_trabajo, categoria_trabajo, orden_de_trabajo, prioridad) VALUES (?,?,?,?,?) ", insert_data
        )

    except Exception as e:
      print 'cserrano.py: Error on line {} '.format(sys.exc_info()[-1].tb_lineno), e

    print 'Cola de trabajos actualizada'
    return
