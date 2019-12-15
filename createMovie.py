import pymysql
import mysql.connector, time
from mysql.connector import Error
from datetime import datetime
import random

def create_mysql_connection(db_user, db_password, host_name, db_name):
    conn = None
    try:
        conn = pymysql.connect(user=db_user, password=db_password, host=host_name, db=db_name)
    except:
        print('connection failed')
    return conn

db = create_mysql_connection(db_user='root', db_password='password', host_name='35.222.44.65', db_name='MoviesMain')
cursor = db.cursor()

now = datetime.now()
createdb_query = "CREATE DATABASE IF NOT EXISTS MoviesMain"
cursor.execute(createdb_query)
db.commit()

cursor.execute("SET FOREIGN_KEY_CHECKS=0")
db.commit()


insert_sql = """CREATE TABLE MoviesMain.customer(
    customer_id int(11) NOT NULL,
    first varchar(255) NOT NULL,
    last varchar(255) NOT NULL,
    genre varchar(255),
    PRIMARY KEY (customer_id)
    )"""
cursor.execute(insert_sql)
db.commit()


insert_sql = """CREATE TABLE MoviesMain.MovieSearches(
    customerID int(11),
    Title TEXT,
    Year INT(11),
    Runtime INT(11),
    Country TEXT,
    Metascore REAL,
    IMDBRating REAL,
    FOREIGN KEY (customerID) REFERENCES customer(customer_id) on delete cascade
    )"""
cursor.execute(insert_sql)
db.commit()

insert_sql = """CREATE TABLE MoviesMain.MovieFavorites(
    customerID int(11),
    Title TEXT,
    Year INT(11), Runtime INT,
    Country TEXT, Metascore REAL,
    IMDBRating REAL,
    FOREIGN KEY (customerID) REFERENCES customer(customer_id) on delete cascade
    )"""
cursor.execute(insert_sql)
db.commit()


insert_sql = """CREATE TABLE MoviesMain.Recommendations(
    customerID int(11),
    Title TEXT,
    Year INT(11),
    Runtime INT(11),
    Country TEXT,
    Metascore REAL,
    IMDBRating REAL,
    FOREIGN KEY (customerID) REFERENCES customer(customer_id) on delete cascade
    )"""
cursor.execute(insert_sql)
db.commit()
