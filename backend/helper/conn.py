from mysql.connector import Error
import mysql.connector

def conn(query, args=(), one=False):
    try:
        with mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="detection"
        ) as db:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query, args)
                result = cursor.fetchall()
                return (result[0] if result else None) if one else result
    except Exception as e:
        return {"error": str(e)}