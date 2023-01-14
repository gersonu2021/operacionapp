#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, g
from pprint import pprint
from settings import models
from modules.excel import Excel
excel = Excel()
from modules.sessions import Sessions
from modules.validate import Validate
validate = Validate()
from modules.custom_logs import Custom_logs
from modules.mailgun import Mailgun
from settings.config import APP_TITLE

login_blueprint = Blueprint('login_blueprint', __name__,
                        template_folder='templates')

@login_blueprint.route('/login/recuperar-clave/', methods=['GET', 'POST'])
def recuperar_clave():
  # Recuperar Clave Paso 3
  if request.args.get('token') and request.args.get('user'):
    token = request.args.get('token')
    user_id = request.args.get('user')
    usuario = g.db.read("SELECT id, email FROM usuarios WHERE id = ? AND token_password = ?", [ int(user_id), str(token) ] )
    if usuario:
      new_password = Validate().random_string(size = 8)
      encoded_password = Validate().md5_encode(new_password)
      g.db.mod("UPDATE usuarios SET password = ? WHERE id = ?", [ encoded_password, int(usuario[0]['id']) ] )

      email = usuario[0]['email']
      href_token = url_for('login_blueprint.login')

      html = " <!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'> <html xmlns='http://www.w3.org/1999/xhtml'> <head> <meta http-equiv='Content-Type' content='text/html; charset=utf-8' /> "
      html += "<style type='text/css'> html{font-size:100%;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%} img {outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;display: block;} a img {border: none;outline: none;} h1 {color: black;} p {color: black;} </style> </head>"
      html += "<body bgcolor='#ffffff' style='margin: 0; padding: 0; min-width: 100%!important;'>"
      html += "<table width='90%' bgcolor='' border='0' cellpadding='0' cellspacing='0' align='center' style='margin-bottom:20px;'>"
      html += "<tr><td>Tu nuevo password es: " + new_password + "</td></tr>"
      html += "<tr><td><br/>Puede entrar y cambiar tu contraseña si lo prefieres en el siguiente <a href='" + href_token + "'>Link</a> </td></tr>"
      html += "</table></body></html>"

      Mailgun().send_html_email(html, email, 'Tu nuevo Password para ' + APP_TITLE)
      return render_template('login.html', section = 'recuperar-clave-3')
    else:
      return str('Token No Válido.')

  # Recuperar Clave Paso 2
  if request.method == 'POST':
    try:
      email = str(request.form['email'])
      if not Validate().email(email):
        raise ValueError('Email no válido')
      usuario = g.db.read("SELECT id FROM usuarios WHERE email = ?", [ email ] )
      if not usuario:
        raise ValueError('Email no válido')
      token_password = Validate().random_string(size = 26)
      g.db.mod("UPDATE usuarios SET token_password = ? WHERE id = ?", 
          [ str(token_password), int(usuario[0]['id']) ] )
    except Exception as e:
      print e
      return str('Email no válido.')

    href_token = str(request.base_url) + "?token=" + str(token_password) + "&user=" + str(usuario[0]['id'])

    html = " <!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'> <html xmlns='http://www.w3.org/1999/xhtml'> <head> <meta http-equiv='Content-Type' content='text/html; charset=utf-8' /> "
    html += "<style type='text/css'> html{font-size:100%;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%} img {outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;display: block;} a img {border: none;outline: none;} h1 {color: black;} p {color: black;} </style> </head>"
    html += "<body bgcolor='#ffffff' style='margin: 0; padding: 0; min-width: 100%!important;'>"
    html += "<table width='90%' bgcolor='' border='0' cellpadding='0' cellspacing='0' align='center' style='margin-bottom:20px;'>"
    html += "<tr><td>Se ha enviado este correo por que haz solicitado una recuperación de tu contraseña.<br/> Si no pediste esto, por favor ignora este mensaje.</td></tr>"
    html += "<tr><td><br/>Para continuar el proceso de recuperación de contraseña por favor haz click sobre este <a href='" + href_token + "'>Link</a> </td></tr>"
    html += "</table></body></html>"

    Mailgun().send_html_email(html, email, 'Recupero de Password ' + APP_TITLE)
    return render_template('login.html', section = 'recuperar-clave-2')

  # Recuperar Clave Paso 1
  return render_template('login.html', section = 'recuperar-clave')

@login_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
  db = g.db
  if request.method == 'POST':
    try:
      email = str(request.form['email'])
      password = str(request.form['password'])
      encoded_password = Validate().md5_encode(password)
    except Exception as e:
      print e
      return render_template('login.html', wrong_password=1)

    user = db.read("SELECT * FROM usuarios WHERE email = ? AND password = ?", (email,encoded_password))
    if user:
      session['user_id'] = int(user[0]['id'])
      Custom_logs().log( filename = 'user_login.log', data = 'ID: ' + str(user[0]['id']) )
      return redirect(url_for('main'))
    else:
      return render_template('login.html', wrong_password=1)
  else:
    return render_template('login.html')

@login_blueprint.route('/logout/')
def logout():
  Sessions().logout_user()
  return redirect(url_for('main'))
