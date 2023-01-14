#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from settings import models
from settings.config import localtime
from modules.excel import Excel
from modules.sessions import Sessions
from pprint import pprint

excel = Excel()

def crear(model):
  if request.method == 'POST':
    response = g.db.d_create_submit(model, request)
    if not response:
      return render_template("errors.html", errors = ['Por favor completa correctamente todos los campos requeridos.'])
    return render_template("default_crear.html", model=model, submited=response)
  data =  g.db.d_create(model)
  return render_template("default_crear.html", data=data, model=model)

def editar(index, model):
  if request.method == 'POST':
    response = g.db.d_edit_submit(model, request, index)
    if response:
      data = None
      return render_template("default_edit.html", data=data, model=model, submited=True)
  data = g.db.d_edit(model, index)
  if (data):
    return render_template("default_edit.html", data=data, model=model)
  else:
    return 'Not Found'

def eliminar(id, model):
  # Check if exist
  for column in model['columns']:
    if column[1] == 'index':
      index = column[0]
  if not index:
    return "Error: no index in model"
  data = g.db.read("SELECT * FROM " + model['table'] +" WHERE " + index + " = ?", [int(id)])
  deleted = False
  # Confirmed | Delete
  if data and request.method == 'POST':
    result = g.db.mod("DELETE FROM " + model['table'] + " WHERE " + index + " = ?", [int(id)])
    deleted = True
  return render_template("default_eliminar.html", model=model, data=data, deleted = deleted)

def file_import(model):
  try:
    len(model['defaults']['import'])
    import_results = excel.import_file(model)
  except Exception as exc:
      return render_template("errors.html", errors = ['No se puede importar la base de datos'])
  return render_template("default_import.html", model=model, import_results=import_results)

def file_export(model):
  try:
    len(model['defaults']['export'])
    export_file = excel.export_model(model, model['defaults']['export'])
  except Exception as exc:
    export_file = None
    return render_template("errors.html", errors = ['No se puede exportar la base de datos'])
  return Response(
    export_file,
    mimetype="text/csv",
    headers={"Content-disposition":"attachment; filename=" + model['table'] + ".xlsx"})
  return render_template("default_export.html", model=model, filename=export_file)

def table_view(search_query, model, settings = ['create', 'edit', 'delete']):
  try:
    search_columns = []
    search = model['defaults']['search']
  except Exception as exc:
    search = None
  if search:
    for item in search:
      for column in model['columns']:
        if item == column[0]:
          search_columns.append(column)

  data = g.db.d_read(model, search, search_query)
  current_url = request.base_url.split("search/", 1)[0]
  return render_template("default.html", model=model, data=data, search_columns = search_columns, current_url = current_url, settings = settings)
