#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys
reload(sys)    # re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')
import os
from flask import Flask, request, redirect, url_for, g
from werkzeug import secure_filename
from settings.config import *
import random, string
from modules.validate import Validate
from pprint import pprint

class Fileupload():

  def __init__(self, 
      upload_folder = None,
      allowed_extensions = None 
      ):
    if not upload_folder:
      upload_folder = app.config['UPLOAD_FOLDER'] 
    if not allowed_extensions:
      allowed_extensions = set(['jpg', 'png', 'gif'])
    self.upload_folder = upload_folder
    self.allowed_extensions = allowed_extensions
    if not os.path.exists(self.upload_folder):
      os.makedirs(self.upload_folder)
    return
  
  def remove_file(self, filename):
    try:
      filepath = os.path.join(self.upload_folder, filename)
      if not os.path.isfile(filepath):
        raise ValueError('File not found: ', filename)
      os.remove(filepath)
    except Exception as e:
      print e
      return False
    return True

  def random_string(self, length = 10):
     return ''.join(random.choice(string.lowercase) for i in range(length))

  def random_filename(self, length = 10, extension = '.jpg'):
    folder = self.upload_folder
    random_string = self.random_string(length)
    random_filename = random_string + extension
    check = os.path.isfile(folder + '/' + random_filename ) 
    while os.path.isfile(folder + '/' + random_filename ):
      random_string = self.random_string()
      random_filename = random_string + extension
    return random_filename

  def upload(self, file):
    # Usage example: filename = file_upload(request.file['somefile'])
    try:
      if not file:
        raise ValueError('File is missing')
      filename = secure_filename(file.filename)
      check = filename.rsplit('.', 1)[1] in self.allowed_extensions
      custom_filename = self.random_filename(
          length = 20,
          extension = '.' + str(filename.rsplit('.', 1)[1]) 
          )
      if not check:
        raise ValueError('Extension not allowd')
    except Exception as e:
      print e
      return False

    try:
      if custom_filename:
        filename = custom_filename
      file.save(os.path.join(self.upload_folder, filename))
      return filename
    except Exception as e:
      print e
      return False

