import create_tables as db

cur = db.cur
conn = db.conn
cur.execute("Select * from IjodiyIsh")
print(cur.fetchall())