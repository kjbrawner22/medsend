from flask import Flask,jsonify,request,redirect
from flask import render_template
import sys
import os
import csv
import sqlite3
import json
import math

app = Flask(__name__)

db_path = os.path.join(app.root_path, "db/database.db")

class User:
  def __init__(self, name):
    self.name = name
    self.requested = ["car", "crutches", "rock"]
    self.requested2 = ["wheelchair", "heelies"]

@app.route('/')
def index():
  create_db()
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  orders = c.execute("SELECT * from donations where date_distributed > 2017-01-01")
  data = c.fetchall()
  donations = donations_dict_arr(data)
  return render_template('index.html', donations=donations)

@app.route('/login', methods=['POST'])
def login():
  print("login",request.form)
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  username = request.form['username']
  password = request.form['password']
  if username == '' or password == '':
    return redirect('/')
  orders = c.execute("SELECT id,type from users where username=? AND password=?",(username,password))
  data = c.fetchall()
  if data == []:
    return redirect('/')
  print(data)
  account_type = data[0][1]
  userid = str(data[0][0])
  if data[0][1] == "donor":
    return redirect('/donor/'+userid)
  else:
    return redirect('/donee/'+userid)

@app.route('/contact')
def contact():
  return render_template('contact.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/new_account', methods=['GET'])
def new_account():
  return render_template('new_account.html')

@app.route('/new_account', methods=['POST'])
def new_acc_login():
  print(request.form)
  new_user = []
  username = request.form['username']
  password = request.form['password']
  password2 = request.form['password2']
  if password != password2 or username == '':
    return redirect('/new_account',method="get")
  new_user.append(request.form['username'])
  new_user.append(password)
  new_user.append(password2)
  new_user.append(type)
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("INSERT INTO users VALUES (?,?,?,?)", new_user)
  return redirect('/donor/4')

@app.route('/donor/<userid>')
def donor(userid):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  orders = c.execute("SELECT * from donations where userid == "+userid+"")
  data = c.fetchall()
  donations = donations_dict_arr(data)
  title = "MedSend"
  orders = c.execute("SELECT * from users where id == "+userid+"")
  data = c.fetchall()
  username = ""
  for d in data:
    username = d[1]

  return render_template('donor.html', username=username,
		                                 title=title,
		                                 donations=donations)

@app.route('/request')
def request_item():
    title = "MedSend"
    user = User('john doe')
    return render_template('request.html', user=user, title=title, donations = donations)

@app.route('/organization/<userid>')
def organization(userid):
    title = "MedSend"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    orders = c.execute("SELECT * from requests where userid == "+userid+"")
    data = c.fetchall()
    requests = requests_dict_arr(data)
    orders = c.execute("SELECT * from users where id == "+userid+"")
    data = c.fetchall()
    username = ""
    for d in data:
      username = d[1]
    return render_template('organization.html', username=username, title=title, requests = requests)

@app.route('/donee/<userid>')
def donee(userid):
    title = "MedSend"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    orders = c.execute("SELECT * from requests where userid == "+userid+"")
    data = c.fetchall()
    requests = requests_dict_arr(data)
    orders = c.execute("SELECT * from users where id == "+userid+"")
    data = c.fetchall()
    username = ""
    for d in data:
      username = d[1]
    return render_template('donee.html', username=username, title=title, requests = requests)


if __name__=='__main__':
  app.run(debug=True)

def requests_dict_arr(data):
  donations= []
  for d in data:
    item = dict()
    item['userid'] = d[0]
    item['item_type'] = d[1]
    item['icon'] = d[2]
    item['image'] = d[3]
    print(d[3])
    item['date_requested'] = d[4]
    item['date_received'] = d[5]
    donations.append(item)
    print(donations)
  return donations

def donations_dict_arr(data):
  donations= []
  for d in data:
    item = dict()
    item['userid'] = d[0]
    item['item_type'] = d[1]
    item['image'] = d[2]
    item['date_donated'] = d[3]
    item['date_distributed'] = d[4]
    donations.append(item)
    print(donations)
  return donations


def create_db():
  conn = sqlite3.connect(db_path)
  conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
  c = conn.cursor()
  # if remaking database.db comment the below 3 lines
  c.execute("DROP TABLE users")
  c.execute("DROP TABLE donations")
  c.execute("DROP TABLE requests")

  c.execute('''CREATE TABLE users
               (id int,
                username text,
                password text,
                type text)''')
  file_name = app.root_path +'/csv/users.csv'
  f = open(file_name,'rt')
  reader = csv.reader(f)
  column_names = True
  for row in reader:
    if column_names:
      column_names = False
      print('ROW SKIPPED',row)
    else:
      c.execute("INSERT INTO users VALUES (?,?,?,?)", row)

  c.execute('''CREATE TABLE donations
               (userid int,
                item_type text,
                image text,
                date_donated text,
                date_distributed text)''')
  file_name = app.root_path+'/csv/donations.csv'
  f = open(file_name,'rt')
  reader = csv.reader(f)
  column_names = True
  for row in reader:
    if column_names:
      column_names = False
      print('ROW SKIPPED',row)
    else:
      c.execute("INSERT INTO donations VALUES (?,?,?,?,?)", row)

  c.execute('''CREATE TABLE requests
               (userid int,
                item_type text,
                icon text,
                image text,
                date_requested text,
                date_received text)''')
  file_name = app.root_path+'/csv/requests.csv'
  f = open(file_name,'rt')
  reader = csv.reader(f)
  column_names = True
  for row in reader:
    if column_names:
      column_names = False
      print('ROW SKIPPED',row)
    else:
      c.execute("INSERT INTO requests VALUES (?,?,?,?,?,?)", row)
  conn.commit()
  f.close()
