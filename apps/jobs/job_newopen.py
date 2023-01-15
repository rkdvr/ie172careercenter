# Usual Dash dependencies
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.exceptions import PreventUpdate
#we use this one for callbacks
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.parse import urlparse, parse_qs
# Let us import the app object in case we need to define
# callbacks here
from app import app
from apps import dbconnect as db
from apps.jobs import job_profile

# PAGE LAYOUT
layout = html.Div(
    [
        html.H2('Add a Job Opening'),
        html.Hr(),
        html.Div(
            [
                html.H4("No jobs available to add a new opening."),
                html.P("Data may still be unavailable or all jobs are already hiring."),
                html.P("Add a new job instead to create a new opening!"), 
                html.Br()
            ],
            id='addjobopen_notice'
        ),
        html.Div(
            [
                #Job Name----------------------------------------------------------------------------
                dbc.Row(
                    [
                        dbc.Label("Job Name", width=2),
                        dbc.Col(
                            html.Div(
                                dcc.Dropdown(
                                    id='jobopen_dropdown',
                                    placeholder = 'Select Job',
                                    clearable=True,
                                    searchable=True,
                                ), 
                                className="dash-bootstrap"
                            ),
                            width=4,
                        ),
                    ],
                    className="m-3"
                ),
                #Job Opening Date------------------------------------------------------------------
                dbc.Row(
                    [
                        dbc.Label("Opening Date", width=2),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                    id='jobopen_opendate',
                            ),
                            width=4,
                        ),
                    ],
                    className="m-3"
                ),
                html.Br(),
                #SUBMIT BUTTON--------------------------------------------------------------
                html.Div(
                    [
                        dbc.Button("Submit", color= 'warning', id='newopen_submitbtn'),
                        dbc.Modal(
                            [
                                dbc.ModalHeader("Saving Progress"),
                                dbc.ModalBody('temp message', id='newopen_feedbackmsg'),
                                dbc.ModalFooter(
                                    dbc.Button(
                                        "Okay", id="newopen_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                                    )
                                ),
                            ],
                            id="newopen_modal",
                            is_open=False,
                        )  
                    ]
                ),
                html.Br(),
            ],
            id = 'newopenpage_div'
        ),
        # ADD NEW JOB BUTTON--------------------------------------------------------------
        html.Div(
            dbc.Button("Add New Job Instead", id="new_job", n_clicks=0, color= 'dark', href="/jobs/jobprofile?mode=add"),
        ),
        html.Br(),
    ]
)

#LOAD JOB DROPDOWN-------------------------------------------------------------------------------
@app.callback(
    [
        Output('jobopen_dropdown', 'options'),
        Output('addjobopen_notice','style'),
        Output('newopenpage_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ]
)
def jobopen_loaddropdown(pathname):
    
    if pathname == '/jobopen/jobnewopen':
        sql = """
            SELECT job_n as label, job_id as value
            FROM jobs
            WHERE job_delete_ind = False and job_s = 'Not Hiring'
        """
        values = []
        cols = ['label', 'value']
        jobdropdownoptions = db.querydatafromdatabase(sql, values, cols)
        job_options = jobdropdownoptions.to_dict('records') #records is the reference of the to_dict function
        
        if job_options:
            jobopennotice = {'display': 'none'}
            newopenpage = None
        else:
            jobopennotice = None
            newopenpage = {'display': 'none'}
            
    else:
        raise PreventUpdate

    return [job_options, jobopennotice, newopenpage]

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("newopen_modal", "is_open"),
        Output("newopen_feedbackmsg", "children"),
        Output("newopen_closebtn", "href")
    ],
    [
        Input("newopen_submitbtn", "n_clicks"),
        Input("newopen_closebtn", "n_clicks"),
    ],
    [
        State('jobopen_dropdown', 'value'),
        State('jobopen_opendate', 'date')
    ]
)

def empprof_submitprocess(submitbtn, closebtn, jobdropdown, jobopendate):
    
    ctx = dash.callback_context
    if ctx.triggered:
        # eventid = name of the element that caused the trigger
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        feedbackmsg = ''
        openmodal = False
        okay_href = None
    else:
        raise PreventUpdate
    
    # Open Submit Modal
    if eventid == 'newopen_submitbtn' and submitbtn:
        openmodal = True

        # check if there are inputs
        inputs = [
            jobopendate,
            jobdropdown
        ] 

        # IF ERRONEOUS INPUTS, RAISE ERROR PROMPT
        if not all(inputs):
            feedbackmsg = "Please provide all inputs correctly."

        # ELSE, SAVE TO DB, EITHER ADD OR EDIT
        else:               
            # UPDATE DB QUERY
            sqlcode = """
            UPDATE jobs
            SET
            job_od = %s,
            job_s = 'Hiring'
            WHERE job_id = %s
            """
            values = [jobopendate, jobdropdown]
            db.modifydatabase(sqlcode,values)

            feedbackmsg = "Job opening created!"
            okay_href = '/jobopen'

    elif eventid == 'newopen_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]