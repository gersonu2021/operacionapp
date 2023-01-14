#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys, os, time, locale
from settings.config import *


class Custom_logs:

  def __init__(self, 
      logs_folder = LOGS_FOLDER, 
      max_file_size = CUSTOM_LOG_FILE_SIZE_LIMIT 
      ):
    self.logs_folder = logs_folder
    self.max_file_size = max_file_size
    return

  def log(self, filename, data):
    filepath = self.logs_folder + "/" + str(filename)
    try:
      # Delete if maxfile reached
      if os.path.isfile(filepath):
        filesize = os.path.getsize(filepath)
        if filesize > self.max_file_size:
          print 'Max file reached.'
          os.remove(filepath)
      # Create new file
      current_time = time.strftime("%d %b %Y %H:%M:%S")
      if not os.path.isfile(filepath):
        with open(filepath,'w') as newfile:
          newfile.write('#Version: 1.0 \n#Date: ' + str(current_time) + ' \n#Fields: time logdata \n')
      # Append Data        
      with open(filepath, "a") as logfile:
        result = logfile.write('[' + str(current_time) + ']' + ' "' + str(data) + '"\n')
        return True
    except Exception as e:
      print e
      return False
