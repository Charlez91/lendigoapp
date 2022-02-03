To run you have to have above python 3.0

Pip install contents of requirements.txt files in your virtual env or use the one here

You can import the sql file into your sql database(e.g mysql, possgress etc) and continue running from there

The lend.json file is a store of all the returned json values from HN

set your environement variables using .env_example as an example for your celery and sqlalchemy backend

test.py contains the algorithms for getting maxitemid, getting items, getting last100items and storage to db.

its not possible to run the schedular without making a background threading event or running as asynchronous task queues

Celery can be used to run the syncing and schedular by uncommenting it and commenting the threading event part

for celery you have to have a redis or rabbitmq url/uri as broker and same or any db as backend to run

for using threading.. which here is set as default.. you dont need any special setting

the api has several routes for get, post, delete and put requests. requests must be made in json format

throwing a GET request to dis 'localhost5000/api/hn/v1'  gets the last 20 items with all the data as addeded

Throwing a POST request to this 'localhost5000/api/hn/v1' posts data dats not in the db to it by the api user

Throwing a GET request to this 'localhost5000/api/hn/v1/allid' gets the last 200 hackernews id added to the db

Throwing A GET request to this 'localhost5000/api/hn/v1/<item_id>' with item_id parsed in gets the whole item with the specified id from db

Throwing a GET request to this 'localhost5000/api/hn/v1/by' with by(author's name) gets the item(s) posted by an author/psoter

Throwing a DELETE request to this 'localhost5000/api/hn/v1/<item_id' with item_id parsed in deletes an item from the db as long as the item was added by an api user and the id exists

Throwing a PUT request to this 'localhost5000/api/hn/v1/item_id' with item_id parsed in updates or edits an item added by an api user