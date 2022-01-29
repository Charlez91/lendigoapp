import requests
import schedule
import json
import requests
import time
import threading
import schedule
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from Lendigo import app, db
#from schedule import every, repeat, run_pending

def get_maxitem():
    url = 'https://hacker-news.firebaseio.com/v0/maxitem.json'
    res = requests.get(url)
    print(res.text)#will comment dis out too
    return res.text

def get_topitem():
    url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    res = requests.get(url)
    print(res.json())#will comment dis out too
    return res.json()

def get_newitem():
    url = 'https://hacker-news.firebaseio.com/v0/newstories.json'
    res = requests.get(url)
    print(res.json())#will comment dis out too
    return res.json()

def get_item(item):
    url = f'https://hacker-news.firebaseio.com/v0//item/{item}.json?print=pretty'
    res = requests.get(url)
    print(res.text)#will comment it out in flask app
    return res.json()

#get last 100 post during which the app was off... the one to be used
#@app.before_request  wrap with this flask app decorator to run on startup of flask app
def concurrent_requests_last100():
    out = []
    CONNECTIONS = 100
    url_list = []
    maxid = int(get_maxitem())
    lastdb_itemid = Item.query.order_by(Item.Item_hnid.desc()).first()
    if maxid-100 <= lastdb_itemid:
        x = lastdb_item + 1
    elif maxid-100 > lastdb_itemid:
        x = maxid - 100
    #x = maxid - 100
    y = maxid + 1
    for x in range(x,y):
        url = f'https://hacker-news.firebaseio.com/v0//item/{x}.json?print=pretty'
        url_list.append(url)
        print(url)
    print(url_list)
    session = requests.Session()
    session.mount(
        'https://',
        requests.adapters.HTTPAdapter(pool_maxsize=CONNECTIONS,
                                      max_retries=3,
                                      pool_block=True)
    )
    def get_requests(url):
        response = session.get(url)
        return response
    with ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        #future_to_url = (executor.submit(get_last10_items, url, TIMEOUT) for url in url_list)
        #future_to_url = (list(executor.map(get_last10_items, TIMEOUT)))
        time1 = time.time()
        for response in list(executor.map(get_requests, url_list)):
            if response.status_code == 200:
                out.append(response.json())
                x = response.json()
                #print(x)
        with open('lend.json', 'w+') as f:
            json.dump(out, f)
            f.close
        time2 = time.time()
        
    #print(f'Took {time2-time1:.2f} s')# will comment out in flask app
    return out

#for the schedulars 5mins run while app is running.... the algorithim to be used
#@repeat(every(5).minutes)
def items_5mins_apart():
    out = []
    CONNECTIONS = 100
    url_list = []
    maxid = int(get_maxitem())
    lastdb_itemid = Item.query.order_by(Item.Item_hnid.desc()).first()
    x = lastdb_itemid + 1
    y = maxid + 1
    for x in range(x,y):
            url = f'https://hacker-news.firebaseio.com/v0//item/{x}.json?print=pretty'
            url_list.append(url)
            print(url)
    print(url_list)
    session = requests.Session()
    session.mount(
        'https://',
        requests.adapters.HTTPAdapter(pool_maxsize=CONNECTIONS,
                                      max_retries=3,
                                      pool_block=True)
    )
    def get_requests(url):
        res = session.get(url)
        return res
    with ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        #future_to_url = (executor.submit(get_last10_items, url, TIMEOUT) for url in url_list)
        #future_to_url = (list(executor.map(get_last10_items, TIMEOUT)))
        time1 = time.time()
        for response in list(executor.map(get_requests, url_list)):
            if response.status_code == 200:
                out.append(response.json())
                x = response.json()
                #print(x)
        with open('lend.json', 'w+') as f:
            json.dump(out, f)
            f.close
        time2 = time.time()
        
    print(f'Took {time2-time1:.2f} s')
    return out

def load_items():
	#with open('lend.json') as f: #alternative to loading the json result is using the json file
	#	x = json.load(f)
    x = items_5mins_apart()
    for data in x:
        if data is not None:
            timestamp = data.get('time')
            dt_object = datetime.fromtimestamp(timestamp)
            items = Item(by = data.get('by'), item_hnid = data.get('id'), title= data.get('title'), text =data.get('text'), 
                         item_type= data.get('type'), time= dt_object, parent= data.get('parent'), kids=str(data.get('kids')),
                         descendants= data.get('descendants'), url= data.get('url'), score= data.get('score'), 
                         deleted= data.get('deleted'), dead= data.get('dead'), apiuser_added= False)
            db.session.add(items)
            db.session.commit()
            #print(items)#comment out in for my flaskapp

schedule.clear()#clear up all old session when i shut down the flask app or restarted in debug
schedule.every(5).minutes.do(load_items)
while True:
    schedule.run_pending()
    time.sleep(1)
