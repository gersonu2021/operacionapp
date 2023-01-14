#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from settings import models
from blueprints import defaults
from modules.sessions import Sessions
from modules.validate import Validate
from pprint import pprint

user_settings = Blueprint('user_settings', __name__,
                        template_folder='templates')

@user_settings.before_request
def check_login():
  from modules.sessions import Sessions
  if Sessions().user['tipo'] != 1:
    return render_template("errors.html", errors = ['No tienes suficientes permisos para entrar a esta sección.'])

@user_settings.route("/user-settings/", methods=['GET', 'POST'])
def main():
  if request.method == 'POST':
    try:
      user = Sessions().user
      if user:
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        email_validation = Validate().email(email)
        telefono = request.form['telefono']
        if nombre and apellido and email and email_validation and telefono:
          g.db.mod("UPDATE usuarios SET nombre = ?, apellido = ?, email = ?, telefono = ? WHERE id = ?", [nombre, apellido, email, telefono, int(user['id'])] )
          return render_template('user_settings.html', section = 'datos-personales', actualizado = True)
        else:
          raise ValueError('Por favor revisa y completa correctamente todos los campos.')
    except Exception as e:
      return render_template('user_settings.html', section = 'datos-personales', error = e)
  return render_template('user_settings.html', section = 'datos-personales')

@user_settings.route("/user-settings/cambio-de-password/", methods=['GET', 'POST'])
def cambio_de_password():
  if request.method == 'POST':
    try:
      user = Sessions().user
      if user:
        password_actual = request.form['password_actual']
        nuevo_password = request.form['nuevo_password']
        confirmacion = request.form['confirmacion']

        if nuevo_password != confirmacion:
          raise ValueError('El nuevo password y la confirmación no cohinciden')

        check = g.db.read("SELECT * FROM usuarios WHERE password = ? and id = ?", [Validate().md5_encode(password_actual), int(user['id'])] )
        if not check:
          raise ValueError('El password es incorrecto')

        if len(password_actual) > 5 and len(nuevo_password) > 5 and len(confirmacion) > 5:
          g.db.mod("UPDATE usuarios SET password = ? WHERE id = ?", [Validate().md5_encode(nuevo_password), int(user['id'])] )
          return render_template('user_settings.html', section = 'cambio-de-password', actualizado = True)
        else:
          raise ValueError('Tu password debe tener un mínimo de 6 caracteres')
    except Exception as e:
      return render_template('user_settings.html', section = 'cambio-de-password', error = e)
  return render_template('user_settings.html', section = 'cambio-de-password')
