import time
import psycopg2
import redis
from flask import Flask, request, render_template

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
dbconn = psycopg2.connect(
    user='postgres',
    password='password',
    host='postgres',
    port= '5432',
    database = "postgres"
)

dbconn.autocommit = True

cursor = dbconn.cursor()

def get_user_count():
    retries = 5
    while True:
        try:
            return cache.incr('user')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        # get user input from html template
        name = request.form.get("name")
        email = request.form.get("email")
        passwd = request.form.get("pass")

        if request.form['action'] == 'save to SQL':
            pg_insert = """ INSERT INTO users (username, email, passwd) VALUES (%s,%s,%s)"""
            inserted_values = (name, email, passwd)
            cursor.execute(pg_insert, inserted_values)
            return "Your information as been added to the database"
        elif request.form['action'] == 'save to Redis':
            count = get_user_count()
            cache.hmset(f"user:{count}", {
                        "name": f"{name}", 
                        "email": f"{email}",
                        "password": f"{passwd}"
                        })
            return "Your information as been added to the cache"
        else:
            return "something broke"
            
    return render_template("index.html")
