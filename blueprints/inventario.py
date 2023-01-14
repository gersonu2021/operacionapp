#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from settings import models
from settings.config import *
from blueprints import defaults
from modules.validate import Validate

from modules.smtpsend import SmtpSend

from pprint import pprint

model = models.inventario
inventario = Blueprint('inventario', __name__, template_folder='templates')

@inventario.before_request
def check_login():
  from modules.sessions import Sessions
  if Sessions().user['tipo'] not in [1,3]:
    return render_template("errors.html", errors = ['No tienes suficientes permisos para entrar a esta sección.'])

@inventario.route('/inventario/retirar/', methods=['GET', 'POST'])
@inventario.route('/inventario/retirar/<index>', methods=['GET', 'POST'])
@inventario.route('/inventario/retirar/<index>/<cantidad>', methods=['GET', 'POST'])
def retirar(index = None, cantidad = 0):
  if not index:
    return render_template("errors.html", errors = ['Error de usuario.'], href = url_for('inventario.main'))
  item = g.db.read("SELECT * FROM inventario WHERE id = ?", [ int(index) ])
  if not item:
    return render_template("errors.html", errors = ['Item no encontrado.'], href = url_for('inventario.main'))
  if cantidad:
    unidades_restantes = int(item[0]['stock']) - int(cantidad)
    if unidades_restantes < 1:
      return render_template( "errors.html", errors = ['No es posible retirar menos que la cantidad disponible'], href = url_for('inventario.retirar', index = int(index)))
    if unidades_restantes < item[0]['cantidad_minima']:
      # Email Send #
      html = """\
          <h1>Aviso de reposisión de inventario.</h1>
      """
      html += "<p>Se ha excedido la cantidad mínima (" + str(item[0]['cantidad_minima']) + ") del item.</p>"
      plain = "Aviso de repo"
      subject = "Aviso de Inventario item: " + str(item[0]['nombre'])

      SmtpSend().send_email(
        plain = plain, 
        html = html, 
        to = 'svalverde@magna.cl', 
        subject = subject)

      alerta_cantidad_minima = 'Se ha excedido la cantidad mínima del item (' + str(item[0]['cantidad_minima']) + '). Se enviará una alerta al administrador para informar reposición.'
          
    else:
      alerta_cantidad_minima = ''

    g.db.mod("UPDATE inventario SET stock = ? WHERE id = ?", [ unidades_restantes, item[0]['id']  ])

    return render_template("success.html", 
        messages = [
          "Se retiraron " + str(cantidad) + " unidades de " + item[0]['nombre'], 
          "Unidades Restantes: " + str(unidades_restantes),
          alerta_cantidad_minima
          ],
          href = url_for('inventario.main') 
        )
  return render_template("inventario.html", 
      section = 'retirar',
      item = item[0]
      )


@inventario.route('/inventario/editar/<index>', methods=['GET', 'POST'])
def editar(index = None):
  if not index:
    return render_template("errors.html", errors = ['Error de usuario.'], href = url_for('inventario.main'))
  return defaults.editar(index, model)

@inventario.route('/inventario/crear/', methods=['GET', 'POST'])
def crear():
  return defaults.crear(model)

@inventario.route('/inventario/', methods=['GET'])
@inventario.route('/inventario/search/<search_query>/', methods=['GET'])
def main(search_query = None):
  #return defaults.table_view(search_query, model)
  if search_query:
    search_query = '%' + str(search_query) + '%'
    data = g.db.read("SELECT id, nombre, sku, cantidad_minima, stock FROM inventario WHERE nombre LIKE ? OR sku LIKE ?", [ search_query, search_query ] )
  else:
    data = g.db.read("SELECT id, nombre, sku, cantidad_minima, stock FROM inventario ORDER BY id DESC LIMIT 50")

  tbody = []
  for row in data:
    tbody.append([ row['id'], row['nombre'], row['sku'], row['stock'], row['cantidad_minima'] ])
  table_data = {
      'thead' : ['Nombre', 'SKU', 'Stock', 'Cantidad Mínima'],
      'tbody' : tbody
      }
  return render_template("inventario.html", 
      table_data = table_data,
      section = 'main'
      )
