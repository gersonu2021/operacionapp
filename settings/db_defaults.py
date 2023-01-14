#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys
reload(sys) # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')
import datetime
from modules.validate import Validate

class DB_defaults:
  def insert_data(self, db):
    check = db.read("SELECT * FROM usuarios LIMIT 1 ")
    if not check:
      print "db_defaults.py: Blank database detected. Creating default entries."
      password_admin = Validate().md5_encode('sRvqMSL0')
      password_maestros = Validate().md5_encode('6c8daRWP')
      password_inventario = Validate().md5_encode('v5dL3TjY')
      password_bodega = Validate().md5_encode('tis5Slmo')
      db.mod("INSERT INTO usuarios (nombre, apellido, password, email, tipo) VALUES (?,?,?,?,?)", 
        [
          ['Admin', 'General', password_admin, 'admin@erpcserrano.cl', 1],
          ['Maestros', 'Magna', password_maestros, 'maestros@erpcserrano.cl', 2],
          ['Admin', 'Inventario', password_inventario, 'inventario@erpcserrano.cl', 3],
          ['Admin', 'Bodega', password_bodega, 'bodega@erpcserrano.cl', 4]
        ])
      db.mod("INSERT INTO categorias_trabajos (nombre, color) VALUES (?, ?)", 
        [
          ['Culatas', '#711E01'], ['Cigueñales', '#3E8ACC'], 
          ['Block', '#BB4945'], ['Bielas','#C1994D'], 
          ['Eje Levas', '#43894E'], ['Varios', '#5A2F60']
        ]
      )
      db.mod("INSERT INTO trabajos (categoria, nombre) VALUES (?, ?)", 
        [
          # Culatas
          [1, 'Rectificar Asientos'],
          [1, 'Rectificar Válvulas'],
          [1, 'Rectificar Superficies'],
          [1, 'Cambiar Guías'],
          [1, 'Probar Presión'],
          [1, 'Hacer Guías'],
          [1, 'Escariar Guías'],
          [1, 'Encamisar Guías'],
          [1, 'Hacer Asientos'],
          [1, 'Barrenar Túnel Eje Levas y Encasquillar'],
          [1, 'Rellenar Sup.'],
          [1, 'Armar Culata - Regular'],
          [1, 'Soldar Culatas'],
          [1, 'Lavado Ultrasonido'],
          [1, 'Otros'],
          [1, 'Otros'],
          # Cigueñales
          [2, 'Rectificar Cig. Banc. Biela'],
          [2, 'Magnaflux - Control de Fisuras'],
          [2, 'Relleno Cig. Banc. Biela'],
          [2, 'Relleno Cig. Axial Pista'],
          [2, 'Enderezar Cig.'],
          [2, 'Pulir'],
          [2, 'Rellenar Espiga Cigueñal'],
          [2, 'Otros'],
          [2, 'Otros'],
          # Block
          [3, 'Rectificar Cilíndros'],
          [3, 'Encamisar Cilíndros'],
          [3, 'Bruñir Cilíndros'],
          [3, 'Barrenar Túnel Cig. Met. Levas'],
          [3, 'Control Túnel Banc.'],
          [3, 'Probar Block a Presión'],
          [3, 'Rectificar Superficie'],
          [3, 'Cambiar Met. Levas - Compensador'],
          [3, 'Probar Bielas y Bancadas'],
          [3, 'Rellenar Ajustes Met. Axial'],
          [3, 'Otros'],
          [3, 'Otros'],
          # Bielas
          [4, 'Rectificar Interior'],
          [4, 'Escuadrar Bielas'],
          [4, 'Escariar Bujes'],
          [4, 'Armar Conj. Biela - Pistón'],
          [4, 'Hacer Bujes Bielas'],
          [4, 'Cambiar Bujes - Encamisar Alojamiento Buje'],
          [4, 'Otros'],
          [4, 'Otros'],
          # Eje Levas
          [5, 'Rectificar Descansos'],
          [5, 'Rectificar Camones'],
          [5, 'Cambiar Piñones Leva - Cic.'],
          [5, 'Rellenar Descansos Balancines'],
          [5, 'Rellenar Camones'],
          [5, 'Rectificar Balancines'],
          [5, 'Otros'],
          [5, 'Otros'],
          # Varios
          [6, 'Rectificar Pistones'],
          [6, 'Escariar Alogamientos Pasados'],
          [6, 'Agrandar Ranuras'],
          [6, 'Sacar Pernos Cortados'],
          [6, 'Repasar - Hacer Hilo Bujías'],
          [6, 'Poner Insertos Hely-Coil'],
          [6, 'Lavar Motor'],
          [6, 'Balancear Cigueñal'],
          [6, 'Otros'],
          [6, 'Otros'],
        ]
      )
      db.mod("INSERT INTO repuestos (nombre) VALUES (?)", 
        [
          # Repuestos #3D3D3D
          ['Juego de Pistones'],
          ['Juego de Anillos'],
          ['Juego de met. de Biela'],
          ['Juego de met. de Bancada'],
          ['Juego de met. de Leva'],
          ['Juego de met. Axial'],
          ['Juego de met. Levas Aux.'],
          ['Pasadores de Pistones'],
          ['Bujes de Bielas'],
          ['Válvulas de Admisión'],
          ['Válvulas de Escape'],
          ['Guías de Válvulas'],
          ['Tapones - Cig.'],
          ['Retenes Válvulas'],
          ['Kits de Camisas'],
          ['Juego Met. Compensador'],
          ['Otros'],
          ['Otros'],
          ['Otros'],
          ['Otros'],
          ['Otros']
        ]
      )
    return 
