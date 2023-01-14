#!/usr/bin/python
# -*- encoding: utf-8 -*-
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings.config import smtp_config
import sys

class SmtpSend:

  def __init__(self, 
      server = smtp_config['SMTPserver'],
      sender = smtp_config['sender'],
      destination = smtp_config['destination'],
      username = smtp_config['username'],
      password = smtp_config['password']
      ):
    self.server = server
    self.sender = sender
    self.destination = destination
    self.username = username
    self.password = password
    return

  def send_email(self, plain, html, to, subject):
      try:
        if not to:
          to = self.destination
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText(plain.encode('utf-8'),'plain','utf-8'))
        msg.attach(MIMEText(html.encode('utf-8'), 'html','utf-8'))
        msg['Subject'] = subject
        msg['From']   = self.sender
        conn = SMTP(self.server)
        conn.starttls() # this is needed for gmail
        conn.set_debuglevel(True)
        conn.login(self.username, self.password)
        try:
          conn.sendmail(self.sender, to, msg.as_string())
        finally:
          conn.quit()
          return True
      except Exception as e:
        errors = str(e) + '\nError on line {}'.format(sys.exc_info()[-1].tb_lineno)
        print errors
        return False
