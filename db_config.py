import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Rahul@103",
        database="cloudshelf_db",
        cursorclass=pymysql.cursors.DictCursor
    )
