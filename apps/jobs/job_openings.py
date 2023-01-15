# Usual Dash dependencies
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from dash import html
import pandas as pd
# Let us import the app object in case we need to define
# callbacks here
from app import app
from apps import dbconnect as db
from apps.jobs import job_applications, job_newopen

layout = html.Div(
    [
        html.H2("Job Openings"),
        html.Hr(),
        html.Div(
            dbc.Row(
                [
                    #SEARCH TRAINING
                    dbc.Col(
                        html.Div(
                            dbc.Input(type="text", id="jobopening_filter", placeholder="🔍 Search Job Openings"),
                        ),                       
                        width=5
                    ),
                    #SEARCH SKILL
                    dbc.Col(
                        html.Div(
                            dbc.Input(type="text", id="skill_filter", placeholder="🔍 Search Skill"),
                        ),                       
                        width=5
                    ),
                    #ADD JOB OPENING -> THIS IS THE FORM TO CHANGE JOB STATUS TO HIRING
                    dbc.Col(
                    html.Div(
                            [
                                dbc.Button("Add Job Opening", id="new_jobopen", n_clicks=0, color= 'warning', href='/jobopen/jobnewopen'),
                            ]
                        )   
                    ),   
                ]
            ),
            style={'vertical-align':'middle'}
        ),
        html.Br(),
        html.Div(
                "This will contain the table for all job openings.",
                id='jobopening_list'
        ),
        html.Br(),
    ]
)

@app.callback(
    [
        Output('jobopening_list','children'),
    ],
    [
        Input('url', 'pathname'),
        Input('jobopening_filter', 'value'),
        Input('skill_filter', 'value')
    ],
    # [
    #     State(),
    # ]
)

def loadjobopenlist (pathname, searchjobopen, searchskill):
    if pathname == '/jobopen':

        #1: QUERY RELEVANT RECORDS
        sql ="""
 			SELECT job_n, dept,  job_ds, job_t, STRING_AGG(skills.sk_n,', '), job_od, jobs.job_id
            FROM jobs
            FULL OUTER JOIN job_skill ON job_skill.job_id = jobs.job_id
            FULL OUTER JOIN skills ON skills.sk_id = job_skill.sk_id
            WHERE job_s = 'Hiring'
                AND job_delete_ind = false
        """
        values = []
        colnames = ['Job Name','Job Department','Description','Tasks', 'Skills Required','Opening Date', 'ID']

        # BEFORE ADDING QUERY IN PGADMIN, ADD FILTER
        if searchjobopen:
            # We use the operator ILIKE for pattern-matching
            sql += "AND job_n ILIKE %s"
            values += [f'%{searchjobopen}%']
        
        sql += "GROUP BY job_n, dept, job_ds, job_t, job_od, jobs.job_id"

        if searchskill:
            sql += " HAVING STRING_AGG(skills.sk_n,', ') ILIKE %s"
            values += [f'%{searchskill}%']

        # RUN MODIFY DB FORMULA
        jobopenlist = db.querydatafromdatabase(sql, values, colnames)

        #2: IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if jobopenlist.shape[0]:
            
            #CREATE EDIT/DELETE BUTTONS COLUMN
            buttons =[]
            for job_id in jobopenlist['ID']:
                buttons += [
                    dbc.Button(
                        "🔍", 
                        color= 'light', 
                        href=f'/jobopen/applications?id={job_id}',
                        size='sm'
                    ),
                ]
            
            #ADD BUTTONS TO joblist TABLE
            jobopenlist['View Applicants'] = buttons
            #REMOVE ID COLUMN -> axis options: 1 - column, 0 - row
            jobopenlist.drop('ID', axis=1, inplace=True) 

            jobopen_table = html.Div(
                dbc.Table.from_dataframe(
                    jobopenlist, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )

            return [jobopen_table]

        # IF EMPTY, RAISE PROMPT
        else:
            return ["No records to display"]
    
    else:
        raise PreventUpdate