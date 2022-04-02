import json
from flask import Flask, request, jsonify
import pymysql
import cv2
import numpy as np
from database import Database

db = Database(dbname='booksite')
# db.createdb()
#db.createTable("CREATE  TABLE booksite.stocks (ISBN int primary key, BookName TEXT, BookAuther TEXT, BookDate TEXT, BookDescription TEXT, BoookCover TEXT, BookTradePrice TEXT, BookRetailPrice TEXT, BookQuantity TEXT);")
# db.createTable("CREATE  TABLE booksite.users (ID int primary key, Username TEXT,Password TEXT, FullName Text, Address TEXT);")
# db.createTable("CREATE TABLE booksite.cart (ID int primary key, username TEXT, isbn TEXT, quantity TEXT);")

'''
1. The name of the book.
2. The author of the book.
3. A data picker allowing the publication date to be set.
4. The ISBN-13 number.
5. The multiline book description.
6. A picture of the front cover.
7. A slider allowing the trade price to be set (max £100).
8. A slider allowing the retail price to be set (max £100).
9. A slider allowing the quantity of books to be set (max 20).
'''
app  = Flask(__name__)


#admin panel
@app.route('/users-login',methods = ['POST'])
def userslogin():
    username = request.form.get('username')
    password = request.form.get('password')
    data = db.SelectQuery('SELECT *  FROM booksite.users WHERE Username = %s AND Password = %s;',param = (username,password))
    if data is None:
        return jsonify({'msg':"Check your username or password OR something went wrong"})
    elif data is not None:
        return jsonify({"msg":f"{data}"})


@app.route('/users-signup',methods=['POST'])
def userssignup():
    
    username = request.form.get('username')
    password = request.form.get('password')
    id = request.form.get('id')
    fullname = request.form.get('fullname')
    address = request.form.get('address')
    db.InsertQuery("Insert into booksite.users(id,Username, Password, Fullname, Address) values (%s, %s, %s, %s, %s)",param = (id,username, password, fullname, address))
    return jsonify({"msg":"Signup Successfull"})
#add and update stocks:: Feature 1
@app.route("/add-stocks",methods= ['POST'])
def AddBook():

    isbn = int(request.form.get('isbn'))
    check_isbn = db.SelectQuery('SELECT * FROM booksite.stocks WHERE ISBN = %s;',param = (isbn),mode = 'fetchone')
    print('---'*10)
    print(check_isbn)
    bookname = request.form.get('bookname')
    author = request.form.get('author')
    bookdate = request.form.get('date')
    bookdescription = request.form.get('desc')
    #----------------
    dir = 'covers/'
    f = request.files.get('cover').read()
    img = np.fromstring(f, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    cv2.imwrite(dir+f"{isbn}_COVER.jpg",img)
    #---------------
    booktradeprice = request.form.get('tradeprice')
    bookretailprice = request.form.get('retailprice')
    bookquantity = int(request.form.get('quantity'))

    if check_isbn is not None:

        db.UpdateQuery('''Update booksite.stocks SET BookName = %s, BookAuther = %s,
                                                                  BookDate = %s, BookDescription = %s, BoookCover = %s,
                                                                  BookTradePrice = %s, BookRetailPrice = %s, BookQuantity = %s 
                                                                  WHERE ISBN = %s;
                                                                  ''' ,param = (bookname, author, bookdate, bookdescription, 
                                                                  dir+f'{isbn}_COVER.jpg', booktradeprice, bookretailprice, bookquantity,isbn))
    elif check_isbn is None:
        db.InsertQuery('''INSERT INTO booksite.stocks (ISBN, BookName, BookAuther,
                                                                  BookDate, BookDescription, BoookCover,
                                                                  BookTradePrice, BookRetailPrice, BookQuantity) 
                                                                  values (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                                                                 
                                                                  ''' ,param = (isbn, bookname, author, bookdate, bookdescription, 
                                                                  dir+f'{isbn}_COVER.jpg', booktradeprice, bookretailprice, bookquantity))
    return jsonify({"msg":True})



#display stocks:: Feature 2
@app.route('/display-stocks-all/',methods = ['GET'])
def display():
    check_isbn = db.SelectQuery('SELECT * FROM booksite.stocks',mode = 'fetchall',param=None)
    return jsonify({'msg':f'{check_isbn}'})


#add to card :: Feature 3
@app.route('/add-to-cart',methods = ['POST'])
def AddToCart():
    #username, isbn, quantity

    id = request.form.get('id')
    username = request.form.get('username')
    isbn = request.form.get('isbn')
    quantity = request.form.get('quantity')

    db.InsertQuery('INSERT INTO booksite.cart(username,isbn,quantity) values(%s, %s, %s);',param = (username, isbn,quantity))

    return jsonify({'msg':'card updated'})

@app.route('/display-cart/<username>',methods = ['GET'])
def DisplayCart(username):
    isbn = []
    cover = []
    price = []
    title = []
    data = db.SelectQuery('SELECT * FROM booksite.cart where username = %s',(username),mode='fetchall')
    for i in data:
        isbn.append(i[2])
    
    for isbn in isbn:
        xdata = db.SelectQuery("SELECT * from booksite.stocks where ISBN = %s",param = (isbn),mode = 'fetchone')
        cover.append(xdata[5])
        price.append(xdata[3])
        title.append(xdata[1])


    return jsonify({"msg":f"Success", 
                    "item image":f"{cover}",
                    "item price":f"{price}",
                    "item name":f"{title}"
                    })

@app.route("/delete-cart",methods=['DELETE'])
def DeleteCart():
    username = request.form.get("username")
    db.DeleteFromRow('DELETE FROM booksite.cart where username = %s',param = (username))
    return jsonify({"msg":"Removed Successfully"})


@app.route("/checkout",methods = ['POST'])
def Checkout():
    username = request.form.get('username')
 
    isbn = []
    quantities = []
    cart_qty = []
    data = db.SelectQuery('SELECT * FROM booksite.cart where username = %s',param = (username),mode = 'fetchall')
    print(data)
    for i in data:
        cart_qty.append(i[-1])
        isbn.append(i[2])
        quantities.append(db.SelectQuery('SELECT BookQuantity FROM booksite.stocks where ISBN = %s',param = (i[2]), mode = 'fetchone')[0])
    print(isbn)
    print(quantities)
    print('-'*10)
    for q_c, q_r,isbn in zip(cart_qty,quantities,isbn):
        print(q_c,q_r,isbn)
        if int(q_c) > int(q_r):
            return jsonify({"msg":f"quantity limit exceeds for {isbn} {q_c} and {q_r}"})
        elif int(q_c) < int(q_r) or int(q_c) == int(q_r):
            i = int(int(q_r) - int(q_c))
            db.UpdateQuery("UPDATE booksite.stocks SET BookQuantity = %s where ISBN = %s",param = (i,isbn))
            db.DeleteFromRow("DELETE FROM booksite.cart where isbn = %s",param=(isbn))
            return jsonify({"msg":f"Success"})
    #update quantity
    #db.UpdateQuery('UPDATE')
    return jsonify({'msg':f'{isbn}'})


if __name__ == '__main__':
    app.run()