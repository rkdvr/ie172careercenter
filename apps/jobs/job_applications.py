# Usual Dash dependencies
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.parse import urlparse, parse_qs
# Let us import the app object in case we need to define
# callbacks here
from app import app

from apps import dbconnect as db
layout = html.Div(
    [
        # html.Div( # This div shall contain all dcc.Store objects
        #     [
        #         dcc.Store(id='application_toload', storage_type='memory', data=0),
        #     ]
        # ),
        html.H2("Application Details", id='dynamic_jobname'),
        html.Hr(),
        #Application Form
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("List of Applicants"),
                        html.Div(
                            "View list of applicants here", id='applicantlist'
                        )
                    ]
                ),
                dbc.Col(
                    [
                        html.H4("List of Qualified Employees"),
                        html.Div(
                            'View list of skilled employees here', id='qualifiedemp'
                        )
                    ]
                ),
            ]
        ),
        html.Br(),
        #ADDING APPLICANTS
        dbc.Row(
            [
                html.Div(
                    [
                        dbc.Button("Add New Applicant", id="add_app", n_clicks=0, color= 'warning'),
                    ]
                )    
            ]
        ),
        html.Br(),
    ]
)

# OUTPUTS UPON PAGE LOAD------------------------------------------------------------
@app.callback(
    [
        Output('dynamic_jobname', 'children'),
        Output('applicantlist','children'),
        Output('qualifiedemp','children'),
        Output("add_app", "href"),
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search'),
    ]
)

def loademployeelist (pathname, search):
    if pathname == '/jobopen/applications':
        parsed = urlparse(search)
        job_id = parse_qs(parsed.query)['id'][0]
        
        #QUERY JOB NAME
        sql_jobname = """
        SELECT job_n
        FROM jobs
        WHERE job_id = %s
        """
        values_jobname = [job_id]
        cols_jobname = ['jobname']
        jobnamevalue = db.querydatafromdatabase(sql_jobname,values_jobname,cols_jobname)
        jobname = jobnamevalue['jobname'][0]
        dynamic_jobname = f'Application Details for {jobname}'

        addapp_href = f"/jobopen/applications/applicantprofile?mode=add&id={job_id}"

        #LIST APPLICANTS-----------------------------------------------------
        #1: QUERY RELEVANT RECORDS
        sql ="""
        SELECT CONCAT(employees.emp_fn,' ',employees.emp_ln), job_apd, applications.job_apid
            FROM applications
            INNER JOIN jobs on applications.job_id = jobs.job_id
            INNER JOIN employees on applications.emp_id = employees.emp_id
        WHERE applications.application_delete_ind = false
            AND jobs.job_delete_ind = false
            AND employees.employee_delete_ind = false
            AND jobs.job_id = %s
        """
        values = [job_id]
        colnames = ['Employee Name', 'Application Date', 'appid']
        applicantlist = db.querydatafromdatabase(sql, values, colnames)

        #2: IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if applicantlist.shape[0]:
            
            #CREATE EDIT/DELETE BUTTONS COLUMN
            buttons =[]
            for job_apid in applicantlist['appid']:
                buttons += [
                    dbc.Button(
                        '⚙️ Edit or Remove', 
                        href=f"/jobopen/applications/applicantprofile?mode=edit&id={job_apid}",
                        size='sm',
                        color='dark'
                    )
                ]
            
            #ADD BUTTONS TO EMPLOYEELIST TABLE
            applicantlist['Action'] = buttons
            #REMOVE ID COLUMN -> axis options: 1 - column, 0 - row
            applicantlist.drop('appid', axis=1, inplace=True) 

            applicant_table = html.Div(
                dbc.Table.from_dataframe(
                    applicantlist, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )
        # IF EMPTY, RAISE PROMPT
        else:
            applicant_table = "No records to display"

        #LIST QUALIFIED EMPLOYEES--------------------------------------------
        #1: QUERY RELEVANT RECORDS
        sql_qualified ="""
        SELECT CONCAT(employees.emp_fn,' ',employees.emp_ln), skills.sk_n, skills.sk_c, employee_skill.sk_l 
            FROM employee_skill
            INNER JOIN skills on employee_skill.sk_id = skills.sk_id
            INNER JOIN employees on employees.emp_id = employee_skill.emp_id
            INNER JOIN job_skill on job_skill.sk_id = employee_skill.sk_id
            INNER JOIN jobs on jobs.job_id = job_skill.job_id
        WHERE jobs.job_id = %s
            AND employee_skill.employee_skill_delete_ind = false
            AND skills.skill_delete_ind = false
            AND employees.employee_delete_ind = false
            AND job_skill.job_skill_delete_ind = false
            AND jobs.job_delete_ind = false
        GROUP BY CONCAT(employees.emp_fn,' ',employees.emp_ln), skills.sk_c, employee_skill.sk_l, skills.sk_n
        """
        values_qualified = [job_id]
        colnames_qualified = ['Employee Name', 'Skill',  'Skill Category', 'Skill Level']

        # RUN MODIFY DB FORMULA
        qualifiedlist = db.querydatafromdatabase(sql_qualified, values_qualified, colnames_qualified)

        #2: IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if qualifiedlist.shape[0]:
            qualifiedemp_table = html.Div(
                dbc.Table.from_dataframe(
                    qualifiedlist, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )
        # IF EMPTY, RAISE PROMPT
        else:
            qualifiedemp_table = "No records to display"

        return [dynamic_jobname, applicant_table, qualifiedemp_table, addapp_href]
    
    else:
        raise PreventUpdate