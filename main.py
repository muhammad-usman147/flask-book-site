from flask import Flask, request 
import pymysql 
from database import Database

db = Database(dbname='booksite')
db.createTable('CREATE TABLE Persons (PersonID int,LastName varchar(255),FirstName varchar(255),Address varchar(255),City varchar(255));')
