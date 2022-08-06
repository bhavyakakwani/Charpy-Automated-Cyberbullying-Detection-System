import mysql.connector
import os
import json

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Password": ""}
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f) 

PASSWORD = configData["Password"]

def create_database():
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD
    )
    cursor = db.cursor()
    cursor.execute("create database if not exists charpy")
    db.close()

    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    cursor.execute("""create table if not exists message_classification(
        message varchar(300) not null,
        predicted varchar(20),
        actual varchar(20)
    )""")
    cursor.execute("""create table if not exists warnings(
        warn_id int unsigned not null auto_increment,
        author_id bigint not null,
        server_id bigint not null,
        message varchar(300) not null,
        type varchar(20) not null,
        primary key(warn_id)
    )""")
    cursor.execute("""create table if not exists logs(
        server_id bigint not null,
        channel_id bigint not null,
        logging bool not null
    )""")
    db.commit()
    db.close()

def check(guild):
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    cursor.execute("""select * from logs where server_id = %s""", (guild.id,))
    result = cursor.fetchall()
    db.close()
    return result