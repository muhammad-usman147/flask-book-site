import json
from flask import Flask, request, jsonify
import pymysql
import cv2
import numpy as np
from database import Database

db = Database(dbname='booksite')
# db.createdb()
# db.createTable('CREATE TABLE booksite.Persons (PersonID int,LastName varchar(255),FirstName varchar(255),Address varchar(255),City varchar(255));')


app  = Flask(__name__)


#admin panel
@app.route("/add-stocks",methods= ['POST'])
def AddBook():

    print(request.form.get('usman'))
    f = request.files.get('cover').read()
    img = np.fromstring(f, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    cv2.imwrite("img.jpg",img)
    return jsonify({"msg":True})

if __name__ == '__main__':
    app.run()