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
# Let us import the app object in case we need to define
# callbacks here
from app import app
from urllib.parse import urlparse, parse_qs
from apps import dbconnect as db
# from apps.jobs import job_profile

layout = html.Div(
    [
        html.Div( # This div shall contain all dcc.Store objects
            [
                dcc.Store(id='jobapp_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Applicant Profile"),
        html.Hr(),
        #EMPLOYEE NAME
        dbc.Row(
            [
                dbc.Label("Employee Name", width=2),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='applicant_dropdown',
                            placeholder = 'Select Employee',
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
        #JOB NAME
        dbc.Row(
            [
                dbc.Label("Job Name", width=2),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='jobapp_dropdown',
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
        #JOB APPLY DATE
        dbc.Row(
            [
                dbc.Label("Date of Application", width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id='jobapp_date',
                    ),
                    width=2,
                ),
            ]
        ),
        html.Br(),
        #DELETE------------------------------------------------------------------------------------
        html.Div(
            [
                dbc.Row(           
                    [
                        dbc.Label("Remove Applicant?", width=2, style={'color': 'red'}),
                        dbc.Col(
                            dbc.Checklist(
                                id='jobapp_removerecord',
                                options=[
                                    {"label": "Yes", "value": 1},
                                ],
                                style={'fontWeight': 'bold', 'color': 'red'}
                            ),
                            width=4
                        ),
                    ],
                    className="mb-3",
                ),
                html.Br(),
            ],
            id='jobapp_removerecord_div',
        ),
        #SUBMIT BUTTON--------------------------------------------------------------
        html.Div(
            [
                dbc.Button("Submit", color= 'warning', id='jobapp_submitbtn'),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Saving Progress"),
                        dbc.ModalBody('temp message', id='jobapp_feedbackmsg'),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Okay", id="jobapp_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                            )
                        ),
                    ],
                    id="jobapp_modal",
                    is_open=False,
                )  
            ]
        )
    ]
)

#lOAD ELEMENTS UPON PAGE LOAD-------------------------------------------------------------------------------
@app.callback(
    [
        Output('jobapp_toload', 'data'),
        Output('jobapp_removerecord_div', 'style'),
        Output('applicant_dropdown', 'options'),
        Output('jobapp_dropdown', 'options'),
        Output('jobapp_dropdown', 'disabled')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def jobapp_loadinfo(pathname, search):
    
    if pathname == '/jobopen/applications/applicantprofile':
        
        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0

        removediv_style = {'display': 'none'} if not to_load else None
        jobapp_disabled = True

        #Query Employee Options
        sql_emp = """
            SELECT concat(emp_fn, ' ', emp_ln) as label, emp_id as value
            FROM employees
            WHERE employee_delete_ind = False
        """
        values_emp = []
        cols_emp = ['label', 'value']
        applicantoptions = db.querydatafromdatabase(sql_emp, values_emp, cols_emp)
        app_options = applicantoptions.to_dict('records') #records is the reference of the to_dict function

        #Query Job Options
        sql_job = """
            SELECT job_n as label, job_id as value
            FROM jobs
            WHERE job_delete_ind = False
        """
        values_job = []
        cols_job = ['label', 'value']
        joboptionstable = db.querydatafromdatabase(sql_job, values_job, cols_job)
        job_options = joboptionstable.to_dict('records') #records is the reference of the to_dict function

    else:
        raise PreventUpdate

    return [to_load, removediv_style, app_options, job_options, jobapp_disabled]

#LOAD DB TO INTERFACE USING SEARCH-------------------------------------------------------------------------------
@app.callback(
    [
        Output('applicant_dropdown', 'value'),
        Output('jobapp_dropdown', 'value'),
        Output('jobapp_date', 'date'),
    ],
    [
        Input('jobapp_toload', 'modified_timestamp'),
    ],
    [
        State('jobapp_toload', 'data'),
        State('url', 'search')
    ]
)

def loadapplicantinfo (timestamp, to_load, search):
    #IF PAGE IS IN EDIT MODE, LOAD ALL VALUES
    parsed = urlparse(search)

    if to_load:
        job_apid = parse_qs(parsed.query)['id'][0]
        
        #QUERY APPLICATION INFO
        sql_appinfo = """
        SELECT applications.emp_id, applications.job_id, job_apd
            FROM applications
            INNER JOIN jobs on applications.job_id = jobs.job_id
            INNER JOIN employees on applications.emp_id = employees.emp_id
        WHERE applications.job_apid = %s
            and employees.employee_delete_ind = False
		    and jobs.job_delete_ind = False
        """
        values_appinfo = [job_apid]
        col_appinfo = ['emp_id','job_id', 'job_apd']
        appinfo_table = db.querydatafromdatabase(sql_appinfo, values_appinfo, col_appinfo)
        applicant_id = int(appinfo_table['emp_id'][0])
        job_applied_id = int(appinfo_table['job_id'][0])
        date_applied = appinfo_table['job_apd'][0]

    #IF PAGE IS IN ADD MODE, LOAD JOB ONLY
    else:
        job_id = parse_qs(parsed.query)['id'][0]

        #QUERY JOB NAME
        job_applied_id = job_id

        #EMPTY VALUES
        applicant_id = None
        date_applied = None

    return [applicant_id, job_applied_id, date_applied]

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("jobapp_modal", "is_open"),
        Output("jobapp_feedbackmsg", "children"),
        Output("jobapp_closebtn", "href")
    ],
    [
        Input("jobapp_submitbtn", "n_clicks"),
        Input("jobapp_closebtn", "n_clicks"),
    ],
    [
        State('applicant_dropdown', 'value'),
        State('jobapp_dropdown', 'value'),
        State('jobapp_date', 'date'),
        State('url', 'search'),
        State('jobapp_removerecord', 'value'),
    ]
)

def empprof_submitprocess(submitbtn, closebtn, 
                        applicant_dropdown, jobapp_dropdown, jobapp_date, 
                        search, jobapp_removerecord):
    

    ctx = dash.callback_context
    if ctx.triggered:
        # eventid = name of the element that caused the trigger
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        feedbackmsg = ''
        openmodal = False
        okay_href = None
    else:
        raise PreventUpdate
    
    # IF SUBMIT BUTTON WAS CLICKED
    if eventid == 'jobapp_submitbtn' and submitbtn:
        # OPEN MODAL
        openmodal = True

        inputs = [
            applicant_dropdown,
            jobapp_dropdown,
            jobapp_date
        ] 

        # IF INVALID INPUTS, RAISE ERROR PROMPT
        if not all(inputs):
            feedbackmsg = "Please provide all inputs."

        # ELIF VALID INPUTS
        else:               
            parsed = urlparse(search)
            mode = parse_qs(parsed.query)['mode'][0]
            
            # IF MODE IS ADD
            if mode == 'add':
                job_id = parse_qs(parsed.query)['id'][0]

                # REF OKAY BUTTON TO PREVIOUS PAGE
                okay_href = f'/jobopen/applications?id={job_id}'

                # SAVE TO DB
                sqlcode = """
                INSERT INTO applications(emp_id,job_id,job_apd)
                VALUES(%s,%s,%s)
                """
                values = [applicant_dropdown, jobapp_dropdown, jobapp_date]
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Applicant added!"

            # ELIF MODE IS EDIT
            elif mode == 'edit':
            # UPDATE DB QUERY
                job_apid = parse_qs(parsed.query)['id'][0]

                sqlcode = """
                UPDATE applications
                SET
                emp_id = %s,
                job_id = %s,
                job_apd = %s,
                application_delete_ind = %s
                WHERE job_apid = %s
                """
                to_delete = bool(jobapp_removerecord) #checking empremove value (either true or false)

                values = [applicant_dropdown, jobapp_dropdown,jobapp_date, to_delete, job_apid]
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "Applicant profile updated!"

                sql_returnid = """
                SELECT job_id
                FROM applications
                WHERE job_apid = %s
                """
                values_returnid = [job_apid]
                cols_returnid = ['job_id']
                returnidvalue = db.querydatafromdatabase(sql_returnid, values_returnid, cols_returnid)
                returnid = returnidvalue['job_id'][0]

                # REF OKAY BUTTON TO PREVIOUS PAGE
                okay_href = f'/jobopen/applications?id={returnid}'

            else:
                raise PreventUpdate #can be a custom url error message
            

    elif eventid == 'jobapp_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]