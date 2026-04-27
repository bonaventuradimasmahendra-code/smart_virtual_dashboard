import mysql.connector

def db_config():
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='cam_py'
    )
    return db

db = db_config()
cursor = db.cursor()

cursor.execute("TRUNCATE TABLE db_cam")
print("Tabel berhasil dikosongkan.")