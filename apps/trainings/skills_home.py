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
from apps.trainings import training_prof

layout = html.Div(
    [
        html.H2("Skills"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        type="text", id="skill_filter", placeholder="🔍 Search a Skill"
                    ),
                    width=4,
                ),
            ]
        ),
        html.Br(),
        html.Div(
                "This will contain the table for all skills.",
                id='skills_list'
        ),
        html.Br(),
        html.Div(
            [
                dbc.Button("Add New Skill", id="add_skill", n_clicks=0, color= 'warning', href='/skills/skillprofile?mode=add'),  
            ]
        )
    ]
)

@app.callback(
    [
        Output('skills_list','children'),
    ],
    [
        Input('url', 'pathname'),
        Input('skill_filter', 'value')
    ],
)

def loadskilllist (pathname, searchskill):
    if pathname == '/skills':

        #1: QUERY RELEVANT RECORDS
        sql ="""
        SELECT sk_n, sk_ds, sk_c, sk_id
        FROM skills
        WHERE skill_delete_ind is False 
        """
        values = []
        colnames = ['Skill', 'Description', 'Skill Category', 'ID']

        # BEFORE ADDING QUERY IN PGADMIN, ADD FILTER
        if searchskill:
            # We use the operator ILIKE for pattern-matching
            sql += "AND sk_n ILIKE %s"
            values += [f"%{searchskill}%"]

        # RUN MODIFY DB FORMULA
        skill_list = db.querydatafromdatabase(sql, values, colnames)

        #2: IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if skill_list.shape[0]:
            
            #CREATE EDIT/DELETE BUTTONS COLUMN
            buttons =[]
            for sk_id in skill_list['ID']:
                buttons += [
                    dbc.Button(
                        '⚙️ Edit or Remove', 
                        href=f"/skills/skillprofile?mode=edit&id={sk_id}",
                        size='sm',
                        color='dark'
                    )
                ]
            
            #ADD BUTTONS TO traininglist TABLE
            skill_list['Action'] = buttons
            #REMOVE ID COLUMN -> axis options: 1 - column, 0 - row
            skill_list.drop('ID', axis=1, inplace=True) 

            skill_table = html.Div(
                dbc.Table.from_dataframe(
                    skill_list, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )

            return [skill_table]

        # IF EMPTY, RAISE PROMPT
        else:
            return ["No records to display"]
    
    else:
        raise PreventUpdate
