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
# from apps.jobs import job_profile

layout = html.Div(
    [
         html.Div( # This div shall contain all dcc.Store objects
            [
                dcc.Store(id='assignment_toload', storage_type='memory', data=0)
            ]
        ),
        html.H2("Assignment Details", id='asnpage_title'),
        html.Hr(),
        #EMPLOYEE NAME
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Employee Name", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='emp_dropdown',
                                placeholder = 'Select Employee',
                                clearable=True,
                                searchable=True,
                            ), 
                            className="dash-bootstrap"
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            id='emp_dropdown_div'
        ),
        #JOB NAME
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Job Name", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='job_dropdown',
                                placeholder = 'Select Job',
                                clearable=True,
                                searchable=True,
                            ), 
                            className="dash-bootstrap"
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            id='job_dropdown_div'
        ),
        #START AND END DATE
        dbc.Row(
            [
                dbc.Label("Start Date", width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id='empjob_start',
                    ),
                    width=2,
                ),
                dbc.Label("End Date", width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id='empjob_end',
                    ),
                    width=2,
                )  
            ],
            className="mb-3",
        ),
        html.Br(),
        #DELETE
        html.Div(
            [
                dbc.Row(           
                    [
                        dbc.Label("Remove Assignment?", width=2, style={'color': 'red'}),
                        dbc.Col(
                            dbc.Checklist(
                                id='assignment_remove',
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
            id='assignment_remove_div',
        ),
        # #ADD TEST MESSAGE
        # html.Div(
        #     [
        #         html.Br(),
        #         html.P("temp message", id='test_message'),
        #     ]
        # ),
        #SUBMIT
        dbc.Button("Submit", color= 'warning', id='assignment_submitbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody('temp message', id='assignment_feedbackmsg'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="assignment_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                    )
                ),
            ],
            id="assignment_modal",
            is_open=False,
        ),
    ]
)

#lOAD ELEMENTS UPON PAGE LOAD-------------------------------------------------------------------------------
@app.callback(
    [
        Output('assignment_toload', 'data'),
        Output('assignment_remove_div', 'style'),
        Output('emp_dropdown', 'options'),
        Output('job_dropdown', 'options'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def loadassignmentprofile(pathname, search):
    
    if pathname == '/employees/employeeprofile/assignmentprofile' or pathname == '/jobs/jobprofile/assignmentprofile':

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None

        #Query Employee Options
        sql_emp = """
            SELECT concat(emp_fn, ' ', emp_ln) as label, emp_id as value
            FROM employees
            WHERE employee_delete_ind = False
        """
        values_emp = []
        cols_emp = ['label', 'value']
        employeeoptions = db.querydatafromdatabase(sql_emp, values_emp, cols_emp)
        emp_options = employeeoptions.to_dict('records') #records is the reference of the to_dict function

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

    return [to_load, removediv_style, emp_options, job_options]

#LOAD DB TO INTERFACE BASED ON MODE-------------------------------------------------------------------------------
@app.callback(
    [
        Output('emp_dropdown', 'value'),
        Output('job_dropdown', 'value'),
        Output('empjob_start', 'date'),
        Output('empjob_end', 'date'),
        # Output('asnpage_title', 'children') #TO ADD NEXT TIME
    ],
    [
        Input('assignment_toload', 'modified_timestamp'),
    ],
    [
        State('assignment_toload', 'data'),
        State('url', 'search'),
        State('url', 'pathname')
    ]
)
def loadassignmentinfo (timestamp, to_load, search, pathname):
    
    #IF PAGE IS IN EDIT MODE, LOAD ALL VALUES, REGARDLESS OF ORIGIN PAGE
    parsed = urlparse(search)

    if to_load:
        asn_id = parse_qs(parsed.query)['id'][0]
        #QUERY APPLICATION INFO
        sql_appinfo = """
        SELECT assignments.emp_id, assignments.job_id, asn_sd, asn_ed
            FROM assignments
            INNER JOIN jobs on assignments.job_id = jobs.job_id
            INNER JOIN employees on assignments.emp_id = employees.emp_id
        WHERE assignments.asn_id = %s
            AND assignments.assignment_delete_ind = false
            AND jobs.job_delete_ind = false
            AND employees.employee_delete_ind = false
        """
        values_asninfo = [asn_id]
        col_asninfo = ['emp_id','job_id', 'asn_sd', 'asn_ed']
        asninfo_table = db.querydatafromdatabase(sql_appinfo, values_asninfo, col_asninfo)
        
        employee_id = int(asninfo_table['emp_id'][0])
        job_assigned_id = int(asninfo_table['job_id'][0])
        asn_start = asninfo_table['asn_sd'][0]
        asn_end = asninfo_table['asn_ed'][0]
        
    #ELIF PAGE IS IN ADD MODE,
    elif to_load == 0:
        loadedID = parse_qs(parsed.query)['id'][0]
        asn_start = None
        asn_end = None

        #IF ORIGIN PAGE IS EMPLOYEE PROFILE
        if pathname == '/employees/employeeprofile/assignmentprofile':
            #lOAD EMP ID
            employee_id = loadedID
            job_assigned_id = None
        #ELIF ORIGIN PAGE IS JOB PROFILE
        elif pathname == '/jobs/jobprofile/assignmentprofile':
            #LOAD JOB ID
            employee_id = None
            job_assigned_id = loadedID      

    else:
        raise PreventUpdate
    
    return [employee_id, job_assigned_id, asn_start, asn_end]

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("assignment_modal", "is_open"),
        Output("assignment_feedbackmsg", "children"),
        Output("assignment_closebtn", "href")
    ],
    [
        Input("assignment_submitbtn", "n_clicks"),
        Input("assignment_closebtn", "n_clicks"),
    ],
    [
        State('emp_dropdown', 'value'),
        State('job_dropdown', 'value'),
        State('empjob_start', 'date'),
        State('empjob_end', 'date'),
        State('url', 'search'),
        State('url', 'pathname'), #NEW
        State('assignment_remove', 'value')
    ]
)
def empprof_submitprocess(submitbtn, closebtn, 
                        empdropdown, jobdropdown, asnstart, asnend,
                        search, pathname, asn_remove):

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
    if eventid == 'assignment_submitbtn' and submitbtn:
        # OPEN MODAL
        openmodal = True

        inputs = [
            empdropdown,
            jobdropdown,
            asnstart,
            asnend
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
                
                returnid = parse_qs(parsed.query)['id'][0]
                # IF ORIGIN PAGE IS EMPPROF
                if pathname == '/employees/employeeprofile/assignmentprofile':
                    # REF OKAY BUTTON TO EMPPROF
                    okay_href = f'/employees/employeeprofile?mode=edit&id={returnid}'
                # ELIF ORIGIN PAGE IS JOBPROF
                elif pathname == '/jobs/jobprofile/assignmentprofile':
                    # REF OKAY BUTTON TO JOBPROF
                    okay_href = f'/jobs/jobprofile?mode=edit&id={returnid}'

                # SAVE TO DB
                sqlcode = """
                INSERT INTO assignments(emp_id,job_id,asn_sd,asn_ed)
                VALUES(%s, %s, %s, %s)
                """
                values = [empdropdown, jobdropdown, asnstart, asnend]
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Assignment added!"

            # ELIF MODE IS EDIT
            elif mode == 'edit':
                # UPDATE DB QUERY
                asn_id = parse_qs(parsed.query)['id'][0]

                sqlcode = """
                UPDATE assignments
                SET
                emp_id = %s,
                job_id = %s,
                asn_sd = %s,
                asn_ed = %s,
                assignment_delete_ind = %s
                WHERE asn_id = %s
                """
                to_delete = bool(asn_remove) #checking asn_remove value (either true or false)

                values = [empdropdown, jobdropdown,asnstart,asnend, to_delete, asn_id]
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "Assignment profile updated!"

                # QUERY EMPID AND JOBID FROM ASNID
                sql_returnid = """
                SELECT emp_id, job_id
                FROM assignments
                WHERE asn_id = %s
                """
                values_returnid = [asn_id]
                cols_returnid = ['emp_id', 'job_id']
                returnidvalue = db.querydatafromdatabase(sql_returnid, values_returnid, cols_returnid)
                emp_id = int(returnidvalue['emp_id'][0])
                job_id = int(returnidvalue['job_id'][0])

                # IF ORIGIN PAGE IS EMPPROF
                if pathname == '/employees/employeeprofile/assignmentprofile':
                    # REF OKAY BUTTON TO EMPPROF
                    okay_href = f'/employees/employeeprofile?mode=edit&id={emp_id}'
                # ELIF ORIGIN PAGE IS JOBPROF
                elif pathname == '/jobs/jobprofile/assignmentprofile':
                    # REF OKAY BUTTON TO JOBPROF
                    okay_href = f'/jobs/jobprofile?mode=edit&id={job_id}'

            else:
                raise PreventUpdate #can be a custom url error message
            
    elif eventid == 'assignment_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]