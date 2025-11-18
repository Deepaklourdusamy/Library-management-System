# This script will create the tables inside an existing database.
# Make sure you have created the database and user in MySQL:
#   CREATE DATABASE library_db;
#   CREATE USER 'library_user'@'localhost' IDENTIFIED BY 'password123';
#   GRANT ALL PRIVILEGES ON library_db.* TO 'library_user'@'localhost';
#   FLUSH PRIVILEGES;
#
# Then run: python database_init.py

import mysql.connector
from mysql.connector import errorcode
from config import DB_CONFIG

schema = """
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    category VARCHAR(100),
    copies INT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    contact VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    member_id INT,
    issue_date DATE,
    return_date DATE,
    fine INT DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE SET NULL
);
"""

def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # execute each statement separated by ';'
        for stmt in schema.split(';'):
            s = stmt.strip()
            if s:
                cursor.execute(s + ';')
        conn.commit()
        cursor.close()
        conn.close()
        print('Database initialized successfully.')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Access denied: check your username/password.')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist. Create database in MySQL and update config.py.')
        else:
            print(err)

if __name__ == '__main__':
    init_db()
