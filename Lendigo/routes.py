import json
import os
import time
import threading
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from Lendigo import app, db, celery
from flask import render_template, jsonify, url_for, flash, redirect, request, abort, Response
from Lendigo.models import Item
from Lendigo.test import *



#celery schedule for async task of scheduling
@celery.task(name='scheduling')
def scheduling():    
    #update db with last 100 items
    load_100items()
    #scheduling the db every 5 minutes syncing
    schedule.clear()#clear up all old session when i shut down the flask app or restarted in debug
    schedule.every(5).minutes.do(load_items)
    while True:
        schedule.run_pending()
        time.sleep(1)
#result = scheduling.delay()# if you decide to use celery uncomment these to run scheduling in celery
#result.wait()#un-comment too


#threading schedule for continous background scheduling execution. either dis or celery
schedule.clear()#comment these till line 62 if you use celery. U either use threading or celery
def run_continuously(interval=300):# or you can set a background threading event
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

#load_100items()#initial run of getting the last 100 items and syncing to db
#schedule.every(5).minutes.do(load_items)#every 5 mins syncing to db
#Start the background thread
#stop_run_continuously = run_continuously()
#Do some other things...
#time.sleep(10)
# Stop the background thread
#stop_run_continuously.set()

#route to run to confirm celery is running
@app.route('/cel')
def celeryrunning():
    scheduling.delay()# it can be run with celery after backend and broker url has been set
    return 'celery is running'


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    items = Item.query.order_by(Item.time.desc()).paginate(page= page, per_page=5)
    #items = Item.query.order_by(Item.time.desc()).filter_by(item_type="story").paginate(page= page, per_page=5)
    return render_template ('home.html', items=items)

@app.route('/about')
def about():
    return render_template ('about.html')

@app.route('/search', methods = ['GET', 'POST'])
def search():
    q= request.args.get('query')#(this is for implementing the dashboard)
    if q:
        items = Item.query.filter(Item.by.contains(q)|
									Item.item_hnid.contains(q)|
									Item.title.contains(q)| Item.text.contains(q))
    return render_template ('search.html', items=items)

@app.route('/story')
def story():
    page = request.args.get('page', 1, type=int)
    items = Item.query.order_by(Item.time.desc()).filter_by(item_type="story").paginate(page= page, per_page=5)
    return render_template ('story.html', items=items)

@app.route('/comment')
def comment():
    page = request.args.get('page', 1, type=int)
    items = Item.query.order_by(Item.time.desc()).filter_by(item_type="comment").paginate(page= page, per_page=5)
    return render_template ('comment.html', items=items)

@app.route('/poll')
def poll():
    page = request.args.get('page', 1, type=int)
    items = Item.query.order_by(Item.time.desc()).filter_by(item_type="poll").paginate(page= page, per_page=5)
    return render_template ('poll.html', items=items)

@app.route('/job')
def job():
    page = request.args.get('page', 1, type=int)
    items = Item.query.order_by(Item.time.desc()).filter_by(item_type="job").paginate(page= page, per_page=5)
    return render_template ('job.html', items=items)

@app.route("/item/<int:item_id>", methods=['GET', 'POST'])
def item(item_id):
	item = Item.query.get_or_404(item_id)
	return render_template('item.html', item=item)


#gets all the items on the db. Post posts to the db
@app.route('/api/hn/v1', methods = ['GET', 'POST'])
def api_v1():
    if request.is_json:
        if request.method == 'GET':    
            items = Item.query.all()
            response = []
            for item in items:
                time = item.time
                timestamp = datetime.timestamp(time)
                data = {"by": item.by, "item_hnid": item.item_hnid, "title": item.title, "text": item.text, 
                        "item_type": item.item_type, "time": timestamp, "parent": item.parents, "kids":item.kids,
                        "descendants": item.descendants, "url": item.url, "score":item.score, 
                        "deleted":item.deleted, "dead": item.dead, "apiuser_added": item.apiuser_added}
                response.append(data)
            #print(response)
            items_20 = response[:20]
            res = {"Items": items_20}
            return jsonify (res), 200
        else:
            #implement algorithm for keys to prevent yeye shitposting
            data = request.get_json()
            dt_object = datetime.utcnow()
            item = Item.query.filter_by(item_hnid= data.get('id')).first()
            if item:
                error_res = {"error":"Item with id already exists. Check id and try again"}
                return jsonify(error_res), 403
            if data.get('id') is None:
                itemid = 0
                res = {"error": "No item id passed in"}
                return jsonify(res), 403
            else:    
                itemid = data.get('id') 
                item_hnid = 22 + itemid
                items = Item(by = data.get('by'), item_hnid = item_hnid, title= data.get('title'), text =data.get('text'), 
                            item_type= data.get('type'), time = dt_object, parents= data.get('parent'), kids=str(data.get('kids')),
                            descendants= data.get('descendants'), url= data.get('url'), score= data.get('score'), 
                                dead= data.get('dead'), apiuser_added= True)
                db.session.add(items)
                db.session.commit()
                time = dt_object
                timestamp = datetime.timestamp(time)
                data = {"by": data.get('by'), "item_hnid": item_hnid, "title": data.get('title'), "text": data.get('text'), 
                            "item_type": data.get('type'),"time":timestamp, "parent": data.get('parent'), "kids":str(data.get('kids')),
                            "descendants": data.get('descendants'), "url": data.get('url'), "score": data.get('score'), 
                                "dead": data.get('dead'), "apiuser_added": True}
                return jsonify (data), 200 
    res = {'error': 'if you see this your request is not json'}	
    return jsonify (res), 400
	 
#returns last 200 ids
@app.route('/api/hn/v1/allid', methods = ['GET'])
def api_v1_ids():
    if request.is_json:
        if request.method == 'GET':
            items = Item.query.all()
            response = []
            for item in items:
                ids = item.item_hnid
                data = response.append(ids)
                response.append(data)
            items_200 = response[:200]
            return jsonify (items_200), 200
    res = {'error': 'if you see this your request is not json'}	
    return jsonify (res), 400

# returns item with id passed in
@app.route('/api/hn/v1/<int:itemid>', methods = ['GET'])
def api_v1_itemid(itemid):
    item = Item.query.filter_by(item_hnid=itemid).first()
    if request.method == 'GET':
        if request.is_json:
            if item:
                time = item.time
                timestamp = datetime.timestamp(time)
                data = {"by": item.by, "item_hnid": item.item_hnid, "title": item.title, "text": item.text, 
                            "item_type": item.item_type, "time": timestamp, "parent": item.parents, "kids":item.kids,
                            "descendants": item.descendants, "url": item.url, "score":item.score, 
                            "deleted":item.deleted, "dead": item.dead, "apiuser_added": item.apiuser_added}
                return jsonify(data), 200
            else:
                data = {'error':'Item not found. Check ID and try again'}
                return jsonify(data), 404
    res = {'error': 'if you see this your request is not json'}	
    return jsonify (res), 400

# returns item(s) with by(author or poster) passed in.
@app.route('/api/hn/v1/<by>', methods = ['GET'])
def api_v1_by(by):
    if request.is_json:
        if request.method == 'GET':
            items = Item.query.filter_by(by=by).all()
            response = []
            for item in items:
                if item:
                    time = item.time
                    timestamp = datetime.timestamp(time)
                    data = {"by": item.by, "item_hnid": item.item_hnid, "title": item.title, "text": item.text, 
                                "item_type": item.item_type, "time": timestamp, "parents": item.parents, "kids":item.kids,
                                "descendants": item.descendants, "url": item.url, "score":item.score, 
                                "deleted":item.deleted, "dead": item.dead, "apiuser_added": item.apiuser_added}
                    response.append(data)
            return jsonify(response), 200
    res = {'error': 'if you see this your request is not json'}	
    return jsonify (res), 400

@app.route('/api/hn/v1/<itemid>', methods = ['DELETE'])
def api_v1_deleteitem(itemid):
    if request.is_json:
        if request.method == 'DELETE':
            item = Item.query.filter_by(item_hnid=itemid).first()
            if item and item.apiuser_added == True:
                db.session.delete(item)
                db.session.commit()
                data = {'status': 'Your Item has been Deleted!'}
                return jsonify(data), 200
            elif item is None:
                data = {'error':'Item not found. Check ID and try again'}
                return jsonify(data), 404
            else:
                data = {'error':'Item cannot be deleted. Check ID and try again. It has to be API added to be able to be deleted'}
                return jsonify(data), 403  
    res = {'error': 'if you see this your request is not json'}	
    return jsonify (res), 400

@app.route('/api/hn/v1/<itemid>', methods = ['PUT'])
def api_v1_updateitem(itemid):
    if request.is_json:
        if request.method == 'PUT':
            item = Item.query.filter_by(item_hnid=itemid).first()
            if item:
                if item.apiuser_added == True:
                    data = request.get_json()
                    item.by = data.get('by')
                    item.item_hnid = itemid
                    item.title = data.get('title')
                    item.text = data.get('text')
                    item.item_type = data.get('type')
                    item.parents= data.get('parent') 
                    item.kids=str(data.get('kids'))
                    item.descendants= data.get('descendants')
                    item.url= data.get('url')
                    item.score= data.get('score')
                    db.session.commit()
                else:
                    data = {'error':'Item cannot be updated. Check ID and try again. It has to be API added to be able to be updated'}
                    return jsonify(data), 403
            else:
                data = {'error':'Item not found. Check ID and try again'}
                return jsonify(data), 404
    res = {'error': 'if you see this your request body is not json'}	
    return jsonify (res), 400
 