from flask import Flask, request 
import pymysql 
from database import Database

db = Database(dbname='booksite')
# db.createdb()
# db.createTable('CREATE TABLE booksite.Persons (PersonID int,LastName varchar(255),FirstName varchar(255),Address varchar(255),City varchar(255));')
