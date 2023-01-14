#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from settings import models
from settings.config import *
from blueprints import defaults
from modules.validate import Validate
import sys
import json
from decimal import Decimal
from pprint import pprint
from modules.smtpsend import SmtpSend
from modules.cserrano import Cserrano

model = models.ordenes_de_trabajo

ordenes_de_trabajo = Blueprint('ordenes_de_trabajo', __name__, template_folder='templates')

@ordenes_de_trabajo.before_request
def check_login():
  from modules.sessions import Sessions
  if Sessions().user['tipo'] != 1:
    return render_template("errors.html", errors = ['No tienes suficientes permisos para entrar a esta sección.'])

############################
# ENVIAR TRABAJO TERMINADO #
############################

@ordenes_de_trabajo.route('/ordenes-de-trabajo/enviar-email-trabajo-terminado/', methods=['GET', 'POST'])
@ordenes_de_trabajo.route('/ordenes-de-trabajo/enviar-email-trabajo-terminado/<index>/', methods=['GET', 'POST'])
def enviar_email_trabajo_terminado(index = None):
  if not index:
    print 'no index'
    return '0'
  try:
    ot = g.db.read("SELECT ordenes_de_trabajo.id, ordenes_de_trabajo.raw, clientes.* "
        "FROM ordenes_de_trabajo "
        "LEFT JOIN clientes "
        "ON clientes.rut = ordenes_de_trabajo.rut_cliente "
        "WHERE ordenes_de_trabajo.id = ?", [ int(index) ] )
    if ot:
      presupuesto = json.loads(ot[0]['raw'])
      cliente = presupuesto['cliente'][0]
      trabajos = presupuesto['trabajos']
      repuestos = presupuesto['repuestos']
    else:
      raise ValueError('Orden de trabajo no se encuentra')
  except Exception as e:
    print 'error: ', e
    return '0'

  # EMAIL TRABAJO TERMINADO #
  logo = request.url_root[:-1] + url_for('static', filename='img/logo-cserrano.png')
  logo_aera = request.url_root[:-1] + url_for('static', filename='img/logo-aera.png')
  logo = 'http://pydev.magna.cl/cserrano/static/img/logo-cserrano.png'
  logo_aera = 'http://pydev.magna.cl/cserrano/static/img/logo-aera.png'
  msg = "  <!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>"
  msg += "  <html xmlns='http://www.w3.org/1999/xhtml'>"
  msg += "  <head>"
  msg += "  <meta http-equiv='Content-Type' content='text/html; charset=utf-8' />"
  msg += "  <title>Cserrano</title>"
  msg += "  <style type='text/css'>"
  msg += "  img {outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;display: block;}"
  msg += "  a img {border: none;outline: none;}"
  msg += "  h1 {color: black;}"
  msg += "  p {color: black;}"
  msg += "  </style>"
  msg += "  </head>"
  msg += "  <body bgcolor='#ffffff' style='margin: 0; padding: 0; min-width: 100%!important;'>"
  msg += "  <table width='100%' bgcolor='' border='0' cellpadding='0' cellspacing='0'>"
  msg += "    <tr>"
  msg += "      <td>"
  msg += "        <p style='text-align:center;'>Estimado Cliente<br/><br/>Le informamos que el trabajo se encuentra listo para su retiro.</p>"
  msg += "      </td>"
  msg += "    </tr>"
  msg += "  <tr><td><p style='text-align:center;'><img style='margin:0 auto; position:relative;' src='%s'/></p></td></tr>" % (logo)
  msg += "  <tr><td><h2 style='font-size:11pt;margin-bottom:20px;text-align:center;'>Nombre:<br/>%s </h2></td></tr>" % (cliente['razon_social'])
  msg += "  <tr><td><h2 style='font-size:11pt;margin-bottom:20px;text-align:center;'>Marca: <br/>%s </h2></td></tr>" % (presupuesto['marca_motor'])
  msg += "  <tr><td><h2 style='font-size:11pt;margin-bottom:20px;text-align:center;'>Folio: <br/>%s </h2></td></tr>" % (index)
  msg += "  </table>"
  msg += "  <table style='width:100%;'>"
  msg += "  <tr>"
  msg += "    <td><p style='width:100%;text-align:center;'>¡GRACIAS POR PREFERIRNOS!<br/></td>"
  msg += "  </tr>"
  msg += "  </table>"
  msg += "  <table style='width:100%;'>"
  msg += "  <tr>"
  msg += "    <td><img style='margin:0 auto; position:relative;' src='%s'/></td>" % (logo_aera)
  msg += "    <td><p style='text-align:left;'>Padre Orellana 1537 <br/>Santiago, Región Metropolitana <br/> Teléfono: 25568622<br/>"
  msg += "    Mail: info@cserrano.cl Web: www.cserrano.cl</p></td>"
  msg += "  </tr>"
  msg += "  </table>"
  msg += "</body></html>"

  # Email Send #
  html = msg
  plain = ""
  subject = "Trabajo Terminado Presupuesto " + str(index)

  #return html

  SmtpSend().send_email(
    plain = plain, 
    html = html, 
    to = cliente['email'], 
    subject = subject)
  return '1'

#####################
# ENVIAR PRESUPESTO #
#####################

@ordenes_de_trabajo.route('/ordenes-de-trabajo/enviar/', methods=['GET', 'POST'])
@ordenes_de_trabajo.route('/ordenes-de-trabajo/enviar/<index>/', methods=['GET', 'POST'])
def enviar(index = None):
  if request.method == 'POST':
    try:
      email = request.form['email']
      ot = int(request.form['ot'])
      presupuesto = g.db.read("SELECT raw, observaciones FROM ordenes_de_trabajo WHERE id = ? ", [ ot ] )
      if not Validate().email(email):
        raise ValueError('Email invalido');
    except Exception as e:
      print e
      return '0'
  else:
    print "No email post"
    return '0'

  if presupuesto:
    try:
      observaciones = presupuesto[0]['observaciones']
      presupuesto = json.loads(presupuesto[0]['raw'])
      pprint(presupuesto)
      cliente = presupuesto['cliente'][0]
      trabajos = presupuesto['trabajos']
      repuestos = presupuesto['repuestos']
      logo = 'http://pydev.magna.cl/cserrano/static/img/logo-cserrano.png'
      #logo = url_for('static', _external=True, filename='img/logo-cserrano.png')
      logo_aera = 'http://pydev.magna.cl/cserrano/static/img/logo-aera.png'
      #logo_aera = url_for('static', _external=True, filename='img/logo-cserrano.png')
    except Exception as e:
      print 'Error on line {} '.format(sys.exc_info()[-1].tb_lineno), e
      return 'Error'
    msg = "  <!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>"
    msg += "  <html xmlns='http://www.w3.org/1999/xhtml'>"
    msg += "  <head>"
    msg += "  <meta http-equiv='Content-Type' content='text/html; charset=utf-8' />"
    msg += "  <title></title>"
    msg += "  <style type='text/css'>"
    msg += "  img {outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;display: block;}"
    msg += "  a img {border: none;outline: none;}"
    msg += "  h1 {color: black;}"
    msg += "  p {color: black;}"
    msg += "  </style>"
    msg += "  </head>"
    msg += "  <body bgcolor='#ffffff' style='margin: 0; padding: 0; min-width: 100%!important;'>"
    msg += "  <table width='100%' bgcolor='' border='0' cellpadding='0' cellspacing='0'>"
    msg += "    <tr>"
    msg += "      <td style='text-align:left;'><img src='%s' alt='Logo Carlos Serrano'/></td>" % (logo)
    msg += "      <td style='text-align:right;'>"
    msg += "        <h1 style='font-size:12pt;'>RECTIFICACIÓN DE MOTORES<br/>CARLOS SERRANO LTDA</h1><br/>"
    msg += "        <p style='font-size:10pt; line-height:16px;'>RUT: 76.055.671.-8<br/>"
    msg += "        Padre Orellana 1537<br/>"
    msg += "        Santiago, Región Metropolitana<br/>"
    msg += "        Teléfono: 2556 8622<br/>"
    msg += "        Email: info@cserrano.cl Web: www.cserrano.cl<br/>"
    msg += "        </p>"
    msg += "      </td>"
    msg += "    </tr>"
    msg += "  <tr><td><h2 style='font-size:11pt;margin-bottom:20px;'>Número de Presupuesto: %s </h2></td></tr>" % (ot)
    msg += "  <tr><td><h2 style='font-size:11pt;margin-bottom:20px;'>Marca Motor: %s </h2></td></tr>" % (presupuesto['marca_motor'])
    msg += "  <tr><td><h2 style='font-size:11pt;margin-bottom:20px;'>Cotización</h2></td></tr>"
    msg += "  <tr style='font-weight:bold;'>"
    msg += "    <td>Señores: %s </td>" % (cliente['razon_social'])
    msg += "    <td>RUT: %s</td>" % (cliente['rut'])
    msg += "  </tr>"
    msg += "  <tr style='font-weight:bold;'>"
    msg += "    <td>Dirección: %s</td>" % (cliente['direccion'])
    msg += "    <td>Teléfono: %s</td>" % (cliente['telefono'])
    msg += "  </tr>"
    msg += "  <tr style='font-weight:bold;'>"
    msg += "    <td>Fecha: %s</td>" % (now_date)
    msg += "  </tr>"
    msg += "  <tr style='font-weight:bold;'>"
    msg += "    <td><p style='font-size:10pt; margin-bottom:20px; margin-top:20px;'>"
    msg += "      Tenemos el agrado de enviar a usted el siguiente presupuesto:</p></td>"
    msg += "  </tr>"
    msg += "  </table>"
    msg += "  <table width='100%' bgcolor='' border='1' cellpadding='0' cellspacing='0' class='table'>"
    msg += "    <thead>"
    msg += "      <tr>"
    msg += "        <th>Ítems</th>"
    msg += "        <th>Codigo</th>"
    msg += "        <th>Cantidad</th>"
    msg += "        <th>Comentario</th>"
    msg += "        <th>Valor Unitario</th>"
    #msg += "        <th>Subtotal</th>"
    msg += "      </tr>"
    msg += "    </thead>"
    msg += "    <tbody>"
    if trabajos:
      msg += "<tr> <td style='font-weight:bold;'>Trabajos</td> </tr>"
      for trabajo in trabajos:
        msg += "      <tr>"
        msg += "        <td>%s</td>" % (trabajo['nombre'])
        msg += "        <td>%s</td>" % (trabajo['codigo'])
        msg += "        <td>%s</td>" % (trabajo['cantidad'])
        msg += "        <td>%s</td>" % (trabajo['comentario'])
        msg += "        <td>%s</td>" % (Validate().format_currency(trabajo['valor_neto']))
        #msg += "        <td>%s</td>" % (Validate().format_currency(trabajo['subtotal']))
        msg += "      </tr>"
    if repuestos:
      msg += "<tr> <td style='font-weight:bold;'>Trabajos</td> </tr>"
      for repuesto in repuestos:
        msg += "      <tr>"
        msg += "        <td>%s</td>" % (repuesto['repuesto'])
        msg += "        <td>%s</td>" % (repuesto['codigo'])
        msg += "        <td>%s</td>" % (repuesto['cantidad'])
        msg += "        <td>%s</td>" % (repuesto['comentario'])
        msg += "        <td>%s</td>" % (Validate().format_currency(repuesto['valor_neto']))
        #msg += "        <td>%s</td>" % (Validate().format_currency(repuesto['subtotal']))
        msg += "      </tr>"
    msg += "      <tr style='font-weight:bold;'>"
    msg += "        <td></td>"
    msg += "        <td></td>"
    msg += "        <td></td>"
    msg += "        <td>Subtotal: </td>"
    msg += "        <td>%s</td>" % (Validate().format_currency(presupuesto['valor_total']))
    msg += "      </tr>"
    msg += "      <tr style='font-weight:bold;'>"
    msg += "        <td></td>"
    msg += "        <td></td>"
    msg += "        <td></td>"
    msg += "        <td>IVA: </td>"
    msg += "        <td>%s</td>" % (Validate().format_currency(presupuesto['iva']))
    msg += "      </tr>"
    msg += "      <tr style='font-weight:bold;'>"
    msg += "        <td></td>"
    msg += "        <td></td>"
    msg += "        <td></td>"
    msg += "        <td>Total: </td>"
    msg += "        <td>%s</td>" % (Validate().format_currency(presupuesto['total']))
    msg += "      </tr>"
    msg += "    </tbody>"
    msg += "  </table>"
    msg += "    <p style='text-align:center;'>Observaciones:<br/>"
    msg += "    <div style='text-align:center;'>%s<br/></div>" % str(observaciones)
    msg += "    <p style='text-align:center;'>Atentamente<br/>"
    msg += "    Carlos Serrano Sánchez</p><br/>"
    msg += "    <p style='text-align:center;'><img style='margin:0 auto; position:relative;' src='%s'/></p>" % (logo_aera)
    msg += "</body></html>"

    # Email Send #
    html = msg
    plain = ""
    subject = "Presupuesto " + str(ot)

    #return html

    SmtpSend().send_email(
      plain = plain, 
      html = html, 
      to = email, 
      subject = subject)
    
    return '1'


  return 'Error: correo no enviado'
  return render_template("ordenes_de_trabajo.html", section="enviado")

#############
# HISTORIAL #
#############

@ordenes_de_trabajo.route('/ordenes-de-trabajo/historial/', methods=['GET', 'POST'])
#@ordenes_de_trabajo.route('/ordenes-de-trabajo/historial/<index>/', methods=['GET', 'POST'])
@ordenes_de_trabajo.route('/ordenes-de-trabajo/historial/search/<search_query>/', methods=['GET', 'POST'])
def historial(search_query = None):
  table_data = {}

  if search_query:
    data = g.db.read("SELECT ordenes_de_trabajo.id, ordenes_de_trabajo.fecha_creacion, ordenes_de_trabajo.valor_total, "
      "ordenes_de_trabajo.rut_cliente, ordenes_de_trabajo.marca_motor, ordenes_de_trabajo.estado, ordenes_de_trabajo.prioritario, "
      "clientes.rut, clientes.email, clientes.telefono, clientes.razon_social, "
      "COUNT(trabajos_orden_de_trabajo.fecha_termino) AS trabajos_terminados, "
      "COUNT(trabajos_orden_de_trabajo.id) AS trabajos "
      "FROM ordenes_de_trabajo "
      "LEFT JOIN clientes "
      "ON ordenes_de_trabajo.rut_cliente = clientes.rut "
      "LEFT JOIN trabajos_orden_de_trabajo "
      "ON ordenes_de_trabajo.id = trabajos_orden_de_trabajo.orden_de_trabajo "
      "WHERE ordenes_de_trabajo.id = ? OR clientes.rut = ? OR clientes.razon_social LIKE ? "
      "GROUP BY ordenes_de_trabajo.id "
      "ORDER BY ordenes_de_trabajo.id DESC LIMIT 5000 ",
      [ search_query, Validate().dni(search_query), '%' + str(search_query) + '%' ]
    )

    tbody = []
    for row in data:
      if row['estado'] == 0:
        row['estado'] = 'Pendiente Aprobación'
      elif row['estado'] == 1:
        row['estado'] = 'Aprobado'
      elif row['estado'] == 2:
        row['estado'] = 'Rechazado'
      elif row['estado'] == 3:
        row['estado'] = 'Retirado y Pagado'
      elif row['estado'] == 4:
        row['estado'] = 'Retirado Sin Cancelar'
      if row['prioritario'] == 1:
        row['prioritario'] = "<i class='fa fa-fw fa-star' style='color:blue;'></i>"
      else:
        row['prioritario'] = ""

      # Estados: 0 Pendiente de Aprobación, 1 Aprobado, 2 Rechazado, 3 Retirado y Pagado, 4 Retirado Sin Cancelar
      tbody.append([ row['id'], row['prioritario'], row['fecha_creacion'], row['razon_social'], row['email'], row['telefono'], row['valor_total'], row['trabajos'], row['trabajos_terminados'], row['marca_motor'], row['estado'] ])
    table_data = {
      'thead' : ['Número', 'Prioritario', 'Fecha', 'Cliente', 'Email', 'Teléfono', 'Valor Total', 'Total Trabajos', 'Trabajos Terminados', 'Marca Motor', 'Estado'],
      'tbody' : tbody
      }

  return render_template(
    "ordenes_de_trabajo.html", 
    section = 'historial', 
    data = table_data
  )

#################
# NUEVO CLIENTE #
#################

@ordenes_de_trabajo.route('/ordenes-de-trabajo/crear/nuevo-cliente/', methods=['GET', 'POST'])
@ordenes_de_trabajo.route('/ordenes-de-trabajo/crear/nuevo-cliente/<rut>', methods=['GET', 'POST'])
def nuevo_cliente(rut = ''):
  if request.method == 'POST':
    try:
      rut = Validate().dni(str(request.form['rut']))
      direccion = str(request.form['direccion'])
      razon_social = str(request.form['razon_social'])
      telefono = str(request.form['telefono'])
      email = str(request.form['email'])
      giro = str(request.form['giro'])
      if email:
        if not Validate().email(email):
          raise ValueError('Email incorrecto')
    except Exception as e:
      print e
      return render_template("errors.html", errors = ['Hay datos incorrectos.'])
    cliente = g.db.read("SELECT id FROM clientes WHERE rut = ?", [ rut ] )
    if cliente:
      return render_template("errors.html", errors = ['El RUT ingresado ya existe en la base de datos.'])
    g.db.mod("INSERT INTO clientes (rut, direccion, razon_social, telefono, email, giro) VALUES (?, ?, ?, ?, ?, ?)", 
        [rut, direccion, razon_social, telefono, email, giro] )
    return render_template("success.html", messages = ['Cliente creado correctamente.'], href = url_for('ordenes_de_trabajo.crear', rut_cliente = rut ))
  else:
    return render_template("ordenes_de_trabajo.html", section="crear-nuevo-cliente", rut = rut)

#############
# FINALIZAR #
#############

@ordenes_de_trabajo.route('/ordenes-de-trabajo/finalizar/<index>', methods=['GET', 'POST'])
def finalizar(index = 0):
  g.db.mod("UPDATE ordenes_de_trabajo SET finalizado = True WHERE id = ?", [ index ] )
  return render_template("success.html", messages = ['La orden de trabajo ha sido finalizada.'], href = url_for('ordenes_de_trabajo.main') )

#########
# CREAR #
#########

# Esta seccion sirve para crear nuevas ordenes de trabajo como tambien para actualizar ordenes de trabajos no aprobadas.
# En el caso de la segunda al momento de actualizar se eliminaran todos los trabajos y repuestos asociadas a estas, pero manteniendo la ot y su numero.
# insertando nuevamente los trabajos y repuestos en la BD

@ordenes_de_trabajo.route('/ordenes-de-trabajo/crear/', methods=['GET', 'POST'])
@ordenes_de_trabajo.route('/ordenes-de-trabajo/crear/<rut_cliente>', methods=['GET', 'POST'])
@ordenes_de_trabajo.route('/ordenes-de-trabajo/crear/ot/<index>/', methods=['GET', 'POST'])
def crear(rut_cliente = None, index = None):

  # Solo si es una edicion de un prosupuesto no aprobado
  ot = None
  if index:
    ot = g.db.read("SELECT * FROM ordenes_de_trabajo WHERE id = ? ", [ index ] )
    if not ot:
      return render_template('errors.html', errors = ['Presupuesto no encontrado'] )
    rut_cliente = ot[0]['rut_cliente']

  try:
    if rut_cliente:
      rut = Validate().dni(str(rut_cliente))
    elif request.args.get('rut_cliente'):
      rut_cliente = Validate().dni(str(request.args.get('rut_cliente')))
    elif request.method == 'POST':
      rut_cliente = Validate().dni(str(request.form['rut']))
    else:
      clientes = g.db.read("SELECT * FROM clientes WHERE estado ")
      return render_template("ordenes_de_trabajo.html", section="crear-ingresar-rut-cliente", clientes = clientes)
  except Exception as e:
    print e
    return render_template('errors.html', errors = ['El cliente no es válido.'] )

  try:
    cliente = g.db.read("SELECT id, rut, direccion, razon_social, giro, telefono, email FROM clientes WHERE rut = ?", [ str(rut_cliente) ] )
  except Exception as e:
    print e
    return render_template("errors.html", errors = ['RUT Incorrecto.'])
  if not cliente:
    return redirect(url_for('ordenes_de_trabajo.nuevo_cliente', rut = rut_cliente ))

  if request.method == 'POST':
    try:
      id_trabajos = request.form.getlist('ids')
      id_repuestos = request.form.getlist('ids_repuestos')
      repuestos_trabajos = request.form.getlist('repuestos')
      aprobacion = request.form['aprobacion']
      marca_motor = request.form['marca_motor']
      observaciones = request.form['observaciones']
      if request.form.getlist('prioritario'):
        prioritario = 1
      else:
        prioritario = 0

      valor_total = 0
      trabajos = []
      repuestos = []
      insert = {
        'trabajos' : [],
        'repuestos' : []
      }

      for id in id_trabajos:
        if request.form['cantidad_' + id]:

          if request.form['valor_neto_' + id]:
            valor_neto = int(request.form['valor_neto_' + id])
          else:
            valor_neto = 0

          try:
            codigo = int(request.form['codigo_' + id])
          except Exception as e:
            print e
            codigo = 0
          trabajos.append({
            'id_trabajo' : id,
            'cantidad' : int(request.form['cantidad_' + id]),
            'nombre' : request.form['nombre_' + id],
            'comentario' : request.form['comentario_' + id],
            'codigo' : codigo,
            'valor_neto' : valor_neto,
            #'subtotal' : valor_neto * int(request.form['cantidad_' + id])
            'subtotal' : valor_neto 
            })
          if request.form['valor_neto_' + id]:
            #valor_total += Decimal(valor_neto) * int(request.form['cantidad_' + id])
            valor_total += Decimal(valor_neto)
          insert['trabajos'].append([int(id), int(request.form['cantidad_' + id]), request.form['comentario_' + id], codigo ,request.form['valor_neto_' + id]])

      for id in id_repuestos:
        if request.form['cantidad_repuesto_' + id]:
          if id in request.form.getlist('recibido_repuesto'):
            recibido = 1
          else:
            recibido = 0

          if request.form['valor_neto_repuesto_' + id]:
            valor_neto = int(request.form['valor_neto_repuesto_' + id])
          else:
            valor_neto = 0

          repuestos.append({
            'id_repuesto' : id,
            'cantidad' : int(request.form['cantidad_repuesto_' + id]),
            'repuesto' : request.form['nombre_repuesto_' + id],
            'comentario' : request.form['comentario_repuesto_' + id],
            'codigo' : request.form['codigo_repuesto_' + id],
            'sobre_medida' : request.form['sobre_medida_repuesto_' + id],
            'repuesto_recibido' : recibido,
            'valor_neto' : valor_neto,
            'subtotal' : valor_neto * int(request.form['cantidad_repuesto_' + id])
           })
          if request.form['valor_neto_repuesto_' + id]:
            valor_total += Decimal(valor_neto) * int(request.form['cantidad_repuesto_' + id])
          insert['repuestos'].append([int(id), request.form['comentario_repuesto_' + id], request.form['codigo_repuesto_' + id], request.form['sobre_medida_repuesto_' + id], int(request.form['cantidad_repuesto_' + id]), recibido, request.form['valor_neto_repuesto_' + id]])

      repuestos_trabajos = str(','.join(repuestos_trabajos))

      iva = valor_total * Decimal(0.19)
      total = valor_total + iva

      raw = {
          'cliente' : cliente,
          'trabajos' : trabajos,
          'repuestos_trabajos' : repuestos_trabajos,
          'repuestos' : repuestos,
          'valor_total' : int(valor_total),
          'iva' : int(iva),
          'total' : int(total),
          'marca_motor' : marca_motor
          }

      # INSERT DATA ON DB #
      if ot:
        numero_orden = ot[0]['id']
        g.db.mod("UPDATE ordenes_de_trabajo SET estado = ? WHERE id = ? ", [ aprobacion, ot[0]['id'] ] )
      else:
        numero_orden = g.db.mod("INSERT INTO ordenes_de_trabajo (rut_cliente, valor_total, observaciones, marca_motor, prioritario, espera_de_repuestos, raw, estado) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
        [ rut_cliente, valor_total, observaciones, marca_motor, prioritario, repuestos_trabajos, json.dumps(raw), aprobacion ])
      if not numero_orden:
        raise ValueError('No se ha guardado la orden de trabajo')

      if insert['trabajos']:
        for row in insert['trabajos']:
          row.append(numero_orden)
        # si se esta editando una ot no aprobada, elimina primero los trabajos
        if ot:
          g.db.mod("DELETE FROM trabajos_orden_de_trabajo WHERE orden_de_trabajo = ? ", [ numero_orden ] )
        g.db.mod("INSERT INTO trabajos_orden_de_trabajo ( trabajo, cantidad, comentario, codigo, valor_neto, orden_de_trabajo ) "
          "VALUES ( ?, ?, ?, ?, ?, ? )", insert['trabajos'] )
      if insert['repuestos']:
        for row in insert['repuestos']:
          row.append(numero_orden)
        # si se esta editando una ot no aprobada, elimina primero los repuestos
        if ot:
          g.db.mod("DELETE FROM repuestos_orden_de_trabajo WHERE orden_de_trabajo = ? ", [ numero_orden ] )
        g.db.mod("INSERT INTO repuestos_orden_de_trabajo ( repuesto, comentario, codigo, sobre_medida, cantidad, recibido, valor_neto, orden_de_trabajo ) " 
          "VALUES ( ?, ?, ?, ?, ?, ?, ?, ? )", insert['repuestos'] )

      session.pop('presupuesto', None)
      session['presupuesto'] = {
          'numero' : numero_orden,
          'presupuesto' : json.dumps(raw)
          }
      print session['presupuesto']['numero']
      #session['presupuesto'] = 'test'

      Cserrano().actualizar_cola(numero_orden)

      return render_template("ordenes_de_trabajo.html", 
         section = 'presupuesto', 
         presupuesto = raw,
         numero_presupuesto = numero_orden,
         observaciones = observaciones
      )

    except Exception as e:
      print 'ordenes_de_trabajo.py: Error on line {} '.format(sys.exc_info()[-1].tb_lineno), e
      return render_template("errors.html", errors = ['Se han ingresado datos incorrectos.'])

  categorias_trabajos = g.db.read("SELECT id, nombre, color FROM categorias_trabajos WHERE estado")
  trabajos = g.db.read("SELECT id, categoria, nombre FROM trabajos "
      "WHERE estado AND categoria IN (SELECT id FROM categorias_trabajos WHERE estado)")
  repuestos = g.db.read("SELECT id, nombre FROM repuestos WHERE estado ")

  data = list(categorias_trabajos)
  for (i, c) in enumerate(data):
    c['trabajos'] = []
    c['cliente'] = cliente[0]
    for trabajo in trabajos:
      if trabajo['categoria'] == c['id']:
        c['trabajos'].append(trabajo)
          
  marcas_motores = g.db.read("SELECT * FROM marcas_motores WHERE estado ")
  if not marcas_motores:
    return render_template('errors.html',  errors = ['No hay marcas de motores creadas.'], href = url_for("ordenes_de_trabajo.main") )
  return render_template(
    "ordenes_de_trabajo.html", 
    section = "detalle-orden-de-trabajo", 
    data = data,
    repuestos = repuestos,
    cliente = cliente[0],
    marcas_motores = marcas_motores
  )

##########
# EDITAR #
##########

@ordenes_de_trabajo.route('/ordenes-de-trabajo/editar/<index>', methods=['GET', 'POST'])
def editar(index = None):
  if request.method == 'POST' and index:
    ot_terminada = g.db.read("SELECT ordenes_de_trabajo.id "
      "FROM ordenes_de_trabajo "
      "WHERE ordenes_de_trabajo.finalizado IS NOT True "
      "AND ordenes_de_trabajo.id NOT IN (SELECT orden_de_trabajo FROM trabajos_orden_de_trabajo WHERE fecha_termino IS NULL) "
      "AND ordenes_de_trabajo.id = ? "
      "ORDER BY id DESC LIMIT 1", [ index ] )
    if ot_terminada:
      return render_template('success.html', messages = ['Los trabajos de esta orden ya están terminados y no puede volver a ser editada.'] )
    try:
      repuestos = request.form.getlist('repuestos')
      repuestos = ','.join(repuestos)
      repuestos_recibidos = request.form.getlist('repuestos_recibidos')
      repuestos_recibidos = str(','.join(repuestos_recibidos))
      observaciones = str(request.form['observaciones'])
      prioritario = request.form.getlist('prioritario') 
      if prioritario:
        prioritario = 1
      else:
        prioritario = 0
      estado = int(request.form['estado'])
      g.db.mod(
        "UPDATE ordenes_de_trabajo SET espera_de_repuestos = ?, observaciones = ?, estado = ?, prioritario = ? "
        "WHERE id = ?",
          [ repuestos, observaciones, estado, prioritario, index ] 
      )
      if repuestos_recibidos:
        g.db.mod( "UPDATE repuestos_orden_de_trabajo SET recibido = 0 WHERE orden_de_trabajo = ? ", [ index ] )
        g.db.mod( "UPDATE repuestos_orden_de_trabajo SET recibido = 1 WHERE id IN (" + repuestos_recibidos + ") AND orden_de_trabajo = ? ", [ index ])
      Cserrano().actualizar_cola(index)
      return render_template("success.html", messages = ['Cambios Guardados.'], href = request.url )
    except Exception as e:
      print 'Error: {} '.format(sys.exc_info()[-1].tb_lineno), e
      return render_template("errors.html", errors = ['No es posible actualizar la orden de trabajo.'], href = request.url )

  if index:
    orden_de_trabajo = g.db.read("SELECT * "
        "FROM ordenes_de_trabajo "
        "WHERE ordenes_de_trabajo.id = ?", 
        [ int(index) ] )
    if not orden_de_trabajo:
      return render_template("errors.html", errors = ['La orden de trabajo seleccionada no se encuentra.'])

  espera_de_repuestos = orden_de_trabajo[0]['espera_de_repuestos']
  ot = json.loads(orden_de_trabajo[0]['raw'])
  ot['observaciones'] = orden_de_trabajo[0]['observaciones']
  ot['marca_motor'] = orden_de_trabajo[0]['marca_motor']
  ot['prioritario'] = orden_de_trabajo[0]['prioritario']
  ot['estado'] = orden_de_trabajo[0]['estado']
  ot['id'] = orden_de_trabajo[0]['id']

  if not ot['trabajos'] and not ot['repuestos']:
    return render_template("errors.html", errors = ['La orden de trabajo seleccionada no tiene Repuestos ni Trabajos.'])

  ids_trabajos = []
  for row in ot['trabajos']:
    ids_trabajos.append(str(row['id_trabajo']))
  ids_trabajos = ','.join(ids_trabajos)

  trabajos = g.db.read(
      "SELECT trabajos.categoria, trabajos.nombre, categorias_trabajos.nombre, "
      "trabajos_orden_de_trabajo.*, maestros.nombre, maestros.id "
      "FROM trabajos_orden_de_trabajo "
      "LEFT JOIN trabajos "
      "ON trabajos.id = trabajos_orden_de_trabajo.trabajo "
      "LEFT JOIN categorias_trabajos "
      "ON trabajos.categoria = categorias_trabajos.id "
      "LEFT JOIN maestros "
      "ON trabajos_orden_de_trabajo.maestro = maestros.id "
      "WHERE trabajos_orden_de_trabajo.orden_de_trabajo = ? ",
      [ index ] 
  )

  ids_categorias = []
  for row in trabajos:
    ids_categorias.append(str(row['categoria']))
  ids_categorias = ','.join(ids_categorias)

  if ids_categorias:
    categorias_trabajos = g.db.read("SELECT id, nombre, color FROM categorias_trabajos WHERE id IN (" + ids_categorias + ")")
  else:
    categorias_trabajos = []

  data = []
  for categoria in categorias_trabajos:
    tmp = []
    if str(categoria['id']) in espera_de_repuestos.split(','):
      categoria['repuestos_trabajos'] = 1
    else:
      categoria['repuestos_trabajos'] = 0
    for trabajo in trabajos:
      if trabajo['categoria'] == categoria['id']:
        tmp.append(trabajo)
    data.append({
      'categoria' : categoria,
      'trabajos' : tmp
      })

  repuestos = g.db.read(
      "SELECT repuestos_orden_de_trabajo.*, repuestos.nombre FROM repuestos_orden_de_trabajo "
      "LEFT JOIN repuestos "
      "ON repuestos_orden_de_trabajo.repuesto = repuestos.id "
      "WHERE orden_de_trabajo = ? "
      , [ index ]
      )

  # Solo prespuesto en estado no aprobado
  if ot['estado'] == 0:
    # Todos los trabajos y repuestos
    categorias_trabajos = g.db.read("SELECT id, nombre, color FROM categorias_trabajos WHERE estado")
    trabajos = g.db.read("SELECT id, categoria, nombre FROM trabajos "
        "WHERE estado AND categoria IN (SELECT id FROM categorias_trabajos WHERE estado)")
    repuestos_todos = g.db.read("SELECT id, nombre FROM repuestos WHERE estado ")
    trabajos_todos = list(categorias_trabajos)
    for (i, c) in enumerate(trabajos_todos):
      c['trabajos'] = []
      for trabajo in trabajos:
        if trabajo['categoria'] == c['id']:
          c['trabajos'].append(trabajo)

    # Completa la informacion de los trabajos con los trabajos de la ot
    for item in trabajos_todos:
      if str(item['id']) in espera_de_repuestos.split(','):
        item['repuestos_trabajos'] = 1
      else:
        item['repuestos_trabajos'] = 0
      for trabajo in item['trabajos']:
        for i1 in data:
          for i2 in i1['trabajos']:
            if trabajo['id'] == i2['trabajo']:
              trabajo['cantidad'] = i2['cantidad']
              trabajo['codigo'] = i2['codigo']
              trabajo['comentario'] = i2['comentario']
              trabajo['valor_neto'] = i2['valor_neto']

    # Completa la info de los repuestos
    for item in repuestos_todos:
      for row in repuestos:
        if row['repuesto'] == item['id']:
          item['cantidad'] = row['cantidad']
          item['codigo'] = row['codigo']
          item['comentario'] = row['comentario']
          item['recibido'] = row['recibido']
          item['sobre_medida'] = row['sobre_medida']
          item['valor_neto'] = row['valor_neto']

    try:
      cliente = g.db.read("SELECT id, rut, direccion, razon_social, giro, telefono, email FROM clientes WHERE rut = ?", [ str(orden_de_trabajo[0]['rut_cliente']) ] )
      if not cliente:
        raise ValueError()
    except:
      return render_template("errors.html", errors = ['Cliente no encontrado.'])

    return render_template(
      "ordenes_de_trabajo_editar_no_aprobados.html",
      ot = ot,
      data = trabajos_todos,
      repuestos = repuestos_todos,
      cliente = cliente
    )

  else:
    return render_template(
      "ordenes_de_trabajo.html", 
      section = 'editar', 
      ot = ot,
      data = data,
      repuestos = repuestos
    )

########
# MAIN #
########

@ordenes_de_trabajo.route('/ordenes-de-trabajo/', methods=['GET'])
def main():
  # Ordenes de trabajo que no tienen trabajos incompletos sin fecha de termino
  data = g.db.read("SELECT ordenes_de_trabajo.id, ordenes_de_trabajo.fecha_creacion, ordenes_de_trabajo.valor_total, "
    "ordenes_de_trabajo.rut_cliente, ordenes_de_trabajo.raw, clientes.rut, clientes.email, clientes.telefono FROM ordenes_de_trabajo "
    "LEFT JOIN clientes "
    "ON ordenes_de_trabajo.rut_cliente = clientes.rut "
    "WHERE ordenes_de_trabajo.finalizado IS NOT True "
    "AND ordenes_de_trabajo.id NOT IN (SELECT orden_de_trabajo FROM trabajos_orden_de_trabajo WHERE fecha_termino IS NULL) "
    "ORDER BY id DESC LIMIT 200")

  tbody = []
  for row in data:
    raw = json.loads(row['raw'])
    tbody.append([ row['id'], row['fecha_creacion'], raw['cliente'][0]['rut'], raw['cliente'][0]['email'], row['telefono'], row['valor_total'] ])
  table_data = {
    'thead' : ['Número', 'Fecha', 'Cliente', 'Email', 'Teléfono', 'Valor Total'],
    'tbody' : tbody
    }
  return render_template(
    "ordenes_de_trabajo.html", 
    section = 'main', 
    data = table_data
  )
