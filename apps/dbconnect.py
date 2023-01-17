import psycopg2
import pandas as pd
import os

def getdblocation():
    DATABASE_URL = os.environ['DATABASE_URL']
    db = psycopg2.connect(DATABASE_URL, sslmode='require')
    return db
    
#     # Define your connection details
#     db = psycopg2.connect(
#         # Get your credentials from the pgadmin. More details below.
#         host='localhost',
#         database='AppProject',
#         user='postgres',
#         port=5432,
#         password='2106'
#     )
#     # return the connection details
#     return db

# used for inserts and updates
def modifydatabase(sql, values):
    db = getdblocation()
    # We create a cursor object
    # Cursor - a mechanism used to manipulate db objects on a per-row basis
    # In this case, a cursor is used to add/edit each row
    cursor = db.cursor()    
    # Execute the sql code with the cursor value
    cursor.execute(sql, values)    
    # Make the changes to the db persistent
    db.commit()
    # Close the connection (so nobody else can use it)
    db.close()

# for SELECT commands
def querydatafromdatabase(sql, values, dfcolumns):    
    # ARGUMENTS
    # sql -- sql query with placeholders (%s)
    # values -- values for the placeholders
    # dfcolumns -- column names for the output
    db = getdblocation()
    cur = db.cursor()
    cur.execute(sql, values)
    rows = pd.DataFrame(cur.fetchall(), columns=dfcolumns)
    db.close()
    return rows

def modifydatabasereturnid(sqlcommand, values):
    # print(sqlcommand,values)
    db = getdblocation()
    cursor = db.cursor()
    cursor.execute(sqlcommand, values)
    key = cursor.fetchone()[0]
    db.commit()
    db.close()
    return key

