import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="E$$@78644",
    database="todo"
    )

cursor = db.cursor(buffered=True)

def all_tasks():
    cursor.execute("SELECT * FROM alltasks")
    return cursor.fetchall()

def general_tasks():
    cursor.execute("SELECT * FROM generalTask")
    return cursor.fetchall()

def campus_tasks():
    cursor.execute("SELECT * FROM campus")
    return cursor.fetchall()

def project_tasks():
    cursor.execute("SELECT * FROM projects")
    return cursor.fetchall()

def learning_tasks():
    cursor.execute("SELECT * FROM learn")
    return cursor.fetchall()

def add_general_task(name, descr):
    cursor.execute("INSERT INTO generalTask (name, descr) VALUES (%s, %s)", (name, descr))
    db.commit()

def add_project_task(name, techStack, descr, level):
    cursor.execute("INSERT INTO projects (name, techStack, descr, level) VALUES (%s, %s, %s, %s)", (name, techStack, descr, level))
    db.commit()

def add_campus_task(name, module, dueDate, task):
    cursor.execute("INSERT INTO campus (name, module, dueDate, descr) VALUES (%s, %s, %s, %s)", (name, module, dueDate, task))
    db.commit()

def add_learning_task(name, lang, descr):
    cursor.execute("INSERT INTO learn (name, lang, descr) VALUES (%s, %s, %s)", (name, lang, descr))
    db.commit()
