#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from modules import models
from config import localtime
from blueprints import defaults

#model = models.home

home = Blueprint('home', __name__, template_folder='templates')

@home.route('/', methods=['GET'])
@home.route('/home', methods=['GET'])
def main(search_query = None):
  return render_template("home.html")
  return render_template("errors.html", errors = ['No tienes permisos suficienes para acceder a esta sección.'])
