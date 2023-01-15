# Usual Dash dependencies
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
# Let us import the app object in case we need to define
# callbacks here
from app import app
from apps import dbconnect as db

layout = html.Div(
    [
        html.H2("Employees"),
        html.Hr(),
        dbc.Row(
            [
                # dbc.Label("Search Title", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="empname_filter", placeholder="🔍 Search Employee"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        html.Br(),
        html.Div(
                "This will contain the table for all employees.",
                id='emp_list'
        ),
        html.Br(),
        html.Div(
            [
                dbc.Button("Add New Employee", id="new_emp", n_clicks=0, color= 'warning', href="/employees/employeeprofile?mode=add")
            ]
        )    
    ]
)

@app.callback(
    [
        Output('emp_list','children'),
    ],
    [
        Input('url', 'pathname'),
        Input('empname_filter', 'value')
    ],
)

def loademployeelist (pathname, searchemployee):
    if pathname == '/employees':

        #1: QUERY RELEVANT RECORDS
        sql ="""
        select concat(emp_fn, ' ', emp_ln), dept, emp_id 
        from employees
        WHERE NOT employee_delete_ind
        """
        values = []
        colnames = ['Employee Name', 'Department', 'ID']

        # BEFORE ADDING QUERY IN PGADMIN, ADD FILTER
        if searchemployee:
            # We use the operator ILIKE for pattern-matching
            sql += "AND concat(emp_fn, ' ', emp_ln) ILIKE %s"
            values += [f"%{searchemployee}%"]

        # RUN MODIFY DB FORMULA
        employeelist = db.querydatafromdatabase(sql, values, colnames)

        #2: IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if employeelist.shape[0]:
            
            #CREATE EDIT/DELETE BUTTONS COLUMN
            buttons =[]
            for emp_id in employeelist['ID']:
                buttons += [
                    dbc.Button(
                        '⚙️ Edit or Remove', 
                        href=f"/employees/employeeprofile?mode=edit&id={emp_id}",
                        size='sm',
                        color='dark'
                    )
                ]
            
            #ADD BUTTONS TO EMPLOYEELIST TABLE
            employeelist['Action'] = buttons
            #REMOVE ID COLUMN -> axis options: 1 - column, 0 - row
            employeelist.drop('ID', axis=1, inplace=True) 

            employee_table = html.Div(
                dbc.Table.from_dataframe(
                    employeelist, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )
            return [employee_table]

        # IF EMPTY, RAISE PROMPT
        else:
            return ["No records to display"]
    
    else:
        raise PreventUpdate