import json
import os
import time
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from Lendigo import app
from flask import render_template, jsonify, url_for, flash, redirect, request, abort, Response
from Lendigo.models import Item



@app.route('/')
@app.route('/home')
def home():
	return render_template ('Lendigo.html')


@app.route('/api/hn/v1', methods = ['GET', 'POST'])
def api_v1():
	if request.method == 'GET':
		if request.is_json:
			data = request.get_json()
			res = {'status':'message received'}
			return jsonify (res), 200
	else:
		if request.is_json:
			data = request.get_json()
			return jsonify (data), 200 
	res = {'error': 'if you see this your request is not json'}	
	return jsonify (res), 200
	 