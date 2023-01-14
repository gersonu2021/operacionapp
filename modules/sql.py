#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys
reload(sys) # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')

import datetime
import re
import sqlite3
import MySQLdb

from flask import Flask, g
from settings.models import models
from modules.excel import Excel
excel = Excel()
from modules.fileupload import Fileupload
from subprocess import Popen, PIPE
from pprint import pprint

#############################
# DATABASE OPERATIONS CLASS #
# svalverde@magna.cl        #
#############################

class Sql:

  def __init__(self, database):
    try:
      self.database = database
    except Exception as exc:
      print "Error: ", exc
      return
    return

#######################
# DATABASE CONNECTION #
#######################

  # mysql command line calls
  def mysql_cmd(self, query):
    try:
      query = "' " + query + " '"
      if self.database['passwd']:
        cmd = "mysql --user " + self.database['user'] + " --password " + self.database['passwd'] + " -e " + query
      else:
        cmd = "mysql -u " + self.database['user'] + " -e " + query
      output = Popen(str(cmd), shell=True, stdout=PIPE).stdout.read()
    except Exception as e:
      print e
    return

  def connect(self):
    # SQLITE
    if self.database['type'] == 'sqlite3':
      conn = sqlite3.connect(self.database['file'], check_same_thread=False)
      conn.row_factory = sqlite3.Row # return data as dictionary instead of tuples (default)
      cursor = conn.cursor()
      self.conn = conn
      self.cursor = cursor
      return conn
    # MYSQL
    if self.database['type'] == 'mysql':
      self.mysql_cmd("CREATE DATABASE IF NOT EXISTS " + self.database['db'])
      try:
        conn = MySQLdb.Connection(
          host=self.database['host'],
          user=self.database['user'],
          passwd=self.database['passwd'],
          port=self.database['port'],
          db=self.database['db'],
          charset='utf8',
          use_unicode=True
        )
        cursor = conn.cursor() # return data in tuple
        cursor = conn.cursor(MySQLdb.cursors.DictCursor) # return data in dictonary instead of tuple
        self.conn = conn
        self.cursor = cursor
      except Exception as e:
        print "Ha ocurrido un error al conectar la base de datos MySQL: ", e
        return False
      return conn

  def disconnect(self):
    try:
      if hasattr(self, 'conn'):
        self.cursor.close()
        self.conn.close()
        del self.conn
        del self.cursor
    except Exception as e:
      print 'Error closing db connection: ', e

##################
# CRUD FUNCTIONS #
##################

  def read(self, query, values = None):
    try:
      self.connect()
      self.cursor
    except Exception as e:
      print e
      print "Error al conectar con la base de datos.", e
      return False
    # SQLITE3
    if self.database['type'] == 'sqlite3':
      if values:
        data = self.cursor.execute(query, self.utf8_decode(values)).fetchall()
      else:
        data = self.cursor.execute(query).fetchall()
      data = self.proxy2list_dict(data) 
    # MYSQL
    if self.database['type'] == 'mysql':
      if values:
        query = query.replace("?", "%s")
        self.cursor.execute(query, self.utf8_decode(values))
        #self.cursor.execute(query, values)
        #print self.cursor._executed # print executed statement
      else:
        data = self.cursor.execute(str(query))

      results = self.cursor.fetchall()
      data = []
      for row in results:
        data.append(row)

    return data

  def mod(self, query, values = None):
    try:
      self.connect()
      self.cursor
    except Exception as e:
      print e
      print "Error al conectar con la base de datos.", e
      return False
    # SQLITE3
    if self.database['type'] == 'sqlite3':
      if values:
        results = self.cursor.execute(query, self.utf8_decode(values))
      else:
        results = self.cursor.execute(query)

    # MYSQL
    if self.database['type'] == 'mysql':
      if values:
        query = query.replace("?", "%s")
        depth = lambda L: isinstance(L, list) and max(map(depth, L))+1
        if depth(values) > 1:
          results = self.cursor.executemany(query, values)
        else:
          results = self.cursor.execute(query, values)
        #print self.cursor._executed # print executed statement
      else:
        results = self.cursor.execute(query)

    self.conn.commit()

    # Return last insert id
    if self.database['type'] == 'sqlite3':
      insert_id = self.read("SELECT LAST_INSERT_ID()")
    if self.database['type'] == 'mysql':
      insert_id = self.cursor.lastrowid
    return insert_id

##################
# MISC FUNCTIONS #
##################

  def utf8_decode(self, values):
    utf8_values = []
    try:
      for value in values:
        #if type(value) is unicode or type(value) is str:
        if isinstance(value, unicode):
          #utf8_values.append(u(value))
          utf8_values.append(value.decode('utf-8'))
        else:
          utf8_values.append(value)
      return utf8_values
    except:
      return values

  # replace python None value for blank string. Rove 'None' strings in jinja2 outputs.
  def replace_nonetype_to_blank(self, data):
    for item in data:
      for key, value in item.iteritems():
        if value is None:
          item[key] = ''
    return data

  # Convert RowProxy to list with dictionaries
  def proxy2list_dict(self, sqlrowproxy):
    data = []
    try:
      for row in sqlrowproxy:
        items = {}
        for key in row.keys():
          items.update({key: row[key]})
        data.append(items)
    except TypeError, te:
      print 'Not valid SQLProxy Object'
    return data

############
# DEFAULTS #
############

  def d_read(self, model, search_columns = None, search_query = None):
    column_fields = []
    for column in model['columns'] :
      if column[0] in model['defaults']['view'] or column[1] == 'index':
        column_fields.append(model['table'] + '.' + column[0])
      if column[1] == 'index':
        index_column = column[0]
    query = "SELECT " + ','.join(column_fields) + " FROM " + model['table'] + " ORDER BY " + index_column + " DESC "

    if search_columns and search_query:
      data = self.search(model, column_fields, search_columns, search_query)
    else:
      data = self.read(query)

    if data:
      data = self.foreign_replace(model, data)

    return data

  def search(self, model, display_columns, search_columns, search_criteria):
  #SELECT * FROM MyTable WHERE (Column1 LIKE '%keyword1%' OR Column2 LIKE '%keyword1%') AND (Column1 LIKE '%keyword2%' OR Column2 LIKE '%keyword2%');
    data = self.read("SELECT " + ','.join(display_columns) + " FROM " + model['table'] + " WHERE " + search_columns[0] + " LIKE ?", ["%" + str(search_criteria) + "%"])
    return data

  def foreign_replace(self, model, data):
    # replace foreign data with WHERE CLAUSE
    if model.has_key('foreigns'):
      for row in data:
        for column in model['columns']:
          #print column[0] + ': ' + str(row[column[0]])
          for foreign in model['foreigns']:
            if column[0] == foreign[1]:
              # Check status of foreign data
              try:
                status_check = self.read("SELECT " + foreign[3] + " FROM " + foreign[2] + " WHERE estado = estado LIMIT 1")
                status_query = " AND (estado OR estado = 'on')"
              except:
                status_query = ""
              foreign_data = None
              if row.has_key(column[0]):
                query = "SELECT " + foreign[2] + "." + foreign[4] + " FROM " + foreign[2] + " WHERE " + foreign[3] + " = '" + str(row[column[0]]) + "'" + status_query + " LIMIT 1"
                foreign_data = self.read(query)
              if foreign_data and row.has_key(column[0]):
                foreign_data = foreign_data[0][foreign[4]]
                row[column[0]] = foreign_data
              else:
                row[column[0]] = ""

      # replace foreign data with JOIN CLAUSE
      #if model.has_key('foreigns'):
      #  for foreign in model['foreigns']:
      #    for column in model['defaults']['view']:
      #      if column == foreign[1]:
      #        column_fields.remove(model['table'] + '.' + column)
      #        foreign_fields.append(foreign[2]+'.'+foreign[4] + " AS " + column)
      #        foreign_joins.append(' INNER JOIN ' + foreign[2] + ' ON ' + model['table'] + '.' + column + ' = ' + foreign[2] + '.' +  foreign[3])
      #  query = "SELECT " + ", ".join(column_fields) + ", " +  ", ".join(foreign_fields) + " FROM " + model['table'] + "".join(foreign_joins)
        # query example query = "SELECT tipos.nombre FROM tipos JOIN bookmarks ON tipos.id = bookmarks.tipo"
      #data = self.read(query)
    return data

  def d_edit(self, model, index):
    data = []
    for column in model['columns']:
      if column[1] == 'index':
        index_column = column[0]
    query = "SELECT " + ','.join(model['defaults']['edit']) + " FROM " + model['table'] + " WHERE " + index_column + " = ?"
    query_results = {'item_data' : self.read( query, [str(int(index))] ) }
    if not query_results:
      return False
    data.append(query_results)

    #normal fields
    for column in model['columns']:
      if column[0] in model['defaults']['edit']:
        skip_column = False
        if model.has_key('foreigns'):
          for foreign_field in model['foreigns']:
            if foreign_field[1] == column[0]:
              skip_column = True
        if not skip_column:
          normal_field = { 'normal_field' : column }
          data.append(normal_field)

    #fields with foreign data
    if model.has_key('foreigns'):
      for field in model['defaults']['edit']:
        for column in model['foreigns']:
          if column[1] == field:
            # check for estado
            try:
              status_check = self.read("SELECT " + column[3] + " FROM " + column[2] + " WHERE estado = estado LIMIT 1")
              status_query = " WHERE estado"
            except Exception as exc:
              status_query = ""

            read = self.read("SELECT " + column[3] + ", " + column[4] + " FROM " + column[2] + status_query)
            data.append( { 'foreign_field' : { 'fields': column, 'items': read } } )


    # Determine and add file type to column
    for row in data:
      if 'normal_field' in row:
        if row['normal_field'][1] == 'file':
          col_name = str(row['normal_field'][0])
          filename = data[0]['item_data'][0][col_name]
          if len(filename) > 3:
            file_extension = '.' + str(filename.rsplit('.', 1)[1]) 
            if file_extension in ['.jpg', '.png', '.gif']:
              row['normal_field'][1] = 'image'
    return data

  def d_edit_submit(self, model, request, index):
    insert_fields, insert_values = [], []
    try:
      fields = model['defaults']['edit']
      required_fields = model['defaults']['required']
    except Exception as e:
      print "Error en la declaración de los campos por defecto en el modelo. ", e
      return False
    edit_fields, insert_values = [], []

    for field in model['defaults']['required']:
      try:
        request.form[field]
      except Exception as e:
        print "Error: el campo " + field + " es obligatorio y no puede estar en blanco, falso o nulo."
        print e
        return False

    for field in model['defaults']['edit']:
      # get column
      for column in model['columns']:
        if field == column[0]:
          break

      # Files Uploads
      if field in request.files:
        try:
          uploaded_file = request.files[str(column[0])]
          if not uploaded_file:
            continue
          filename = Fileupload().upload(uploaded_file)
          if filename:
            insert_fields.append( field +  " = " + "?" )
            insert_values.append( filename )
            # delete old file after upload new one
            old_file = g.db.read("SELECT " + field + " FROM " + model['table'] + " WHERE id = " + str(int(index)) )  
            Fileupload().remove_file(old_file[0][field])
        except Exception as e:
          print e
      # Normal field
      elif field in request.form:
        insert_fields.append( field +  " = " + "?" )
        if column[1] == 'boolean' or column[1] == 'estado':
          if field:
            insert_values.append( 1 )
          else:
            insert_values.append( 0 )
        else:
          insert_values.append( request.form[field] )
      else:
        insert_values.append( False )

    query = "UPDATE " + model['table'] + " SET " + ', '.join(insert_fields) + " WHERE id = " + str(int(index))
    results = self.mod(query, insert_values)
    return 1

  def d_create(self, model):
    data = []
    for field in model['defaults']['edit']:
      #normal fields
      for column in model['columns']:
        if column[0] == field:
          skip_column = False
          if model.has_key('foreigns'):
            for foreign_field in model['foreigns']:
              if foreign_field[1] == column[0]:
                skip_column = True

          if not skip_column:
            normal_field = { 'normal_field' : column }
            data.append(normal_field)

    #fields with foreign data
    if model.has_key('foreigns'):
      for field in model['defaults']['edit']:
        for column in model['foreigns']:
          if column[1] == field:
            # check for estado
            try:
              status_check = self.read("SELECT " + column[3] + " FROM " + column[2] + " WHERE estado = estado LIMIT 1")
              if status_check:
                status_query = " WHERE estado OR estado = 'on'"
              else:
                status_query = ""
            except Exception as e:
              print 'error', e

            read = self.read("SELECT " + column[3] + ", " + column[4] + " FROM " + column[2] + status_query)
            data.append( { 'foreign_field' : { 'fields': column, 'items': read } } )

    data.append({'item_data' : None})
    return data

  def validate_fields(self, model, request):
    required_fields = model['defaults']['required']
    for field in required_fields:
      try:
        value = request.form[field]
      except Exception as exc:
        print 'Error al validar el campo:', str(field)
        print exc
        return False
      for column in model['columns']:
        if column[0] == field:
          if (column[1] == 'status' or column[1] == 'estado') and (value == '1' or value == '0'):
            pass
          elif (column[1] == 'text' or column[1] == 'textarea') and value:
            pass
          elif column[1] == 'url' and value:
            pass
          elif column[1] == 'date' or column[1] == 'fecha' and value:
            pass
          elif column[1] == 'integer' and value:
            try:
              int(value)
              pass
            except Exception as exc:
              print exc
              return False
          elif column[1] == 'boolean' or column[1] == 'status':
            try:
              bool(value)
              pass
            except Exception as e:
              print e
              return False
            pass
          else:
            print "validation field error: ", field, ", ", value
            return False
    return True

  def d_create_submit(self, model, request):
    # pendiente: no dejar avanzar si faltan los campos requeridos
    if not self.validate_fields(model, request):
      return False
    fields = model['defaults']['edit']
    insert_fields, insert_values = [], []
    for field in model['defaults']['edit']:
      for column in model['columns']:
        if field == column[0]:
          break
      insert_fields.append( "?" )
      # Files Uploads
      if column[1] == 'file':
        try:
          uploaded_file = request.files[str(column[0])]
          filename = Fileupload().upload(uploaded_file)
          insert_values.append( filename )
        except Exception as e:
          print e
      # Prepare normal data for insert
      elif field in request.form:
        if column[1] == 'boolean' or column[1] == 'estado':
          if field:
            insert_values.append( 1 )
          else:
            insert_values.append( 0 )
        else:
          insert_values.append( request.form[field] )
      else:
        insert_values.append( "" )

    query = "INSERT INTO " + model['table'] + " ("+', '.join(fields)+") VALUES ("+', '.join(insert_fields)+")"

    results = self.mod(query, insert_values)
    return 1

########################
# MODELS AUTO CREATION #
########################

  def create_all(self, models):
    for key, value in models.iteritems():
      try:
        # check if database exists
        table_exists = self.read(
        "SELECT TABLE_NAME "
        "FROM information_schema.tables "
        "WHERE table_schema = '" + str(self.database['db']) + "' "
        "AND table_name = '" + str(key) + "' "
        "LIMIT 1");
        # create table
        if not table_exists:
          self.create(value)
        # check if every column in model exists on every table
        columns = self.read("DESCRIBE " + str(key));
        column = [col['Field'] for col in columns]
        for col in value['columns']:
          if str(col[0]) not in column:
            raise ValueError( "column: " + str(col[0]) + " not found on table: " + str(key), "Check your model declaration and rebuild table is recommended." )
            #print "column: " + str(col[0]) + " not found on table: " + str(key)
            #print "Check your model declaration and rebuild table is recommended."
      except Exception as exc:
        print key + ": Database model creating error.", exc

    return

  def create(self, model):
    try:
      #self.mod("DROP TABLE IF EXISTS " + model['table'])
      query = []
      for item in model['columns']:
        try:
          if not str(item[3]):
            raise ValueError('empty default value')
          default_value = "DEFAULT " + str(item[3])
        except:
          default_value = ""

        # SQLITE3 DATATYPES #
        if self.database['type'] == 'sqlite3':
          if item[1] == 'index':
              query.append(item[0] + " INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE" )
          elif item[1] == 'boolean' or item[1] == 'status':
            # sqlite3 no tiene campos tipo booleanos
            query.append(item[0] + " INTEGER " + default_value)
          elif item[1] == 'text' or item[1] == 'url' or item[1] == 'textarea':
            query.append(item[0] + " TEXT " + default_value)
          elif item[1] == 'integer':
            query.append(item[0] + " INTEGER " + default_value)
          elif item[1] == 'date' or item[1] == 'fecha':
            if default_value == 'DEFAULT CURRENT_TIMESTAMP':
              default_value = "DEFAULT (datetime('now','localtime'))"
            query.append(item[0] + " DATE " + default_value)

        # MYSQL DATATYPES #
        if self.database['type'] == 'mysql':
          if item[1] == 'index':
              query.append(item[0] + " INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE" )
          elif item[1] == 'boolean' or item[1] == 'status':
            query.append(item[0] + " BOOLEAN " + default_value)
          elif item[1] == 'text' or item[1] == 'url' or item[1] == 'textarea':
            query.append(item[0] + " TEXT " + default_value)
          elif item[1] == 'email':
            query.append(item[0] + " VARCHAR(254) " + default_value)
          elif item[1] == 'integer':
            query.append(item[0] + " INTEGER " + default_value)
          elif item[1] == 'percentage':
            query.append(item[0] + " VARCHAR(6) " + default_value)
          elif item[1] == 'date' or item[1] == 'fecha':
            # fecha_creacion: "creation_time"     DATETIME DEFAULT CURRENT_TIMESTAMP,
            # fecha_modificacion: "modification_time" DATETIME ON UPDATE CURRENT_TIMESTAMP
            if default_value == 'DEFAULT CURRENT_TIMESTAMP':
              query.append(item[0] + " TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            else:
              query.append(item[0] + " DATE " + default_value)
          elif item[1] == 'timestamp':
            query.append(item[0] + " TIMESTAMP " + default_value)
          elif item[1] == 'datetime':
            query.append(item[0] + " DATETIME " + default_value)
          else:
            query.append(item[0] + " TEXT " + default_value)
            
      query = ', '.join(query)
      query = "CREATE TABLE IF NOT EXISTS " + model['table'] + "(" + query + ");"
      self.mod(str(query))

      # Add Indexes:
      if 'indexes' in model:
        try:
          for index in model['indexes']:
            query = "ALTER TABLE %s ADD INDEX %s (%s) " % ( model['table'], index, index )
            self.mod(query)
        except Exception as e:
          print 'ERROR: sql.py index creation error on table: \'%s\' index: \'%s:\' %s' % ( model['table'], index, str(e) )

      excel.generate_example(model)
    except Exception as e:
      print 'Error creating table in database: {} '.format(sys.exc_info()[-1].tb_lineno), e
      return
    return


