#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from modules import models
from config import localtime
from blueprints import defaults

model = models.ciudades

ciudades = Blueprint('ciudades', __name__, template_folder='templates')

@ciudades.route('/ciudades/crear/', methods=['GET', 'POST'])
def crear(): 
    return defaults.crear(model)
    #return render_template("errors.html", errors = ['No tienes permisos suficienes para acceder a esta sección.'])

@ciudades.route('/ciudades/editar/<index>', methods=['GET', 'POST'])
def editar(index=None):
  return defaults.editar(index, model)

@ciudades.route('/ciudades/eliminar/<id>', methods=['GET', 'POST'])
def eliminar(id=None):
  return defaults.eliminar(id, model)

@ciudades.route('/ciudades/import/', methods=['GET', 'POST'])
def file_import():
  return defaults.file_import(model)

@ciudades.route('/ciudades/export/', methods=['GET', 'POST'])
def file_export():
  return defaults.file_export(model)

@ciudades.route('/ciudades/')
@ciudades.route('/ciudades/search/<search_query>', methods=['GET'])
def main(search_query = None):
  return defaults.table_view(search_query, model)
