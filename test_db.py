import apps.dbconnect as db
from datetime import datetime

def addfewemps():
    # We use the function modifydatabase() -- it has 2 arguments
    # The first argument is the sql code, where we use a placeholder %s
    # The second argument is ALWAYS a list of values to replace the %s in the sql code
    sqlcode = """ 
    INSERT INTO employees (EMP_FN, EMP_LN, EMP_SSS, EMP_ADR, DEPT)
    VALUES (%s, %s, %s, %s, %s)
    """ 
    # The %s are known as placeholders for the values to place in the db.
    # Using placeholders is a good way to avoid “SQL INJECTION” into the db

    # Better than directly adding variables into the sql string
    # importing datetime object from the datetime package (i know confusing)
    # so we can get current the current date and time
    # The order of values on this list must correspond to the query above
    # If the SQL has no placeholders, use an empty list (i.e. [])

    #db is the alias for dbconnect
    db.modifydatabase(sqlcode, ['Leila','Crisostomo','513113121','Quezon City','Production'])
    db.modifydatabase(sqlcode, ['Cola','Cobarrubias','256118826','Quezon City','Operations'])
    db.modifydatabase(sqlcode, ['Erika','De Vera','239487398','Quezon City','IT'])
    db.modifydatabase(sqlcode, ['Irene','Mutuc','309837435','Pasig City','Operations'])
    # Just some feedback that the code succeeded
    print('done!')

sql_resetemps = """
    TRUNCATE TABLE employees RESTART IDENTITY CASCADE
"""
db.modifydatabase(sql_resetemps, [])
addfewemps()

# querydatafromdatabase(sql, values, dfcolumns):
sql = 'SELECT * FROM employees'
values = []
colnames = ['EMP_ID', 'EMP_FN', 'EMP_LN', 'EMP_SSS', 'EMP_ADR', 'DEPT', 'EMPLOYEE_DELETE_IND']

print(db.querydatafromdatabase(sql, values, colnames))