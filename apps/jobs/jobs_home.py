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
# from apps.jobs import job_profile

job_openings = [
    dbc.CardBody(
        [
            html.H2("Card title", className="card-title", id='current_job_open'),
            # html.P("This is some card content that we'll reuse", className="card-text",),
        ],
        style={'text-align': 'center'}
    ),
    html.Div(
        [
            dbc.Button("View Job Openings Report", color="light", id="opening_btn", n_clicks=0),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Current Job Openings Report")),
                    dbc.ModalBody(
                        "This will contain the table for current job openings.", 
                        id='currentopen_list'
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "See More at Job Openings Page", id="jobopen_closebtn", 
                            className="ms-auto", n_clicks=0, color= 'warning',
                            href='/jobopen'
                        )
                    ),
                ],
                id="opening_modal",
                size="xl",
                is_open=False,
            ),
        ],
        className="d-grid gap-2",
    ),
]
current_assignments = [
    dbc.CardBody(
        [
            html.H2("Card title", className="card-title", id='current_job_asn'),
            # html.P("This is some card content that we'll reuse", className="card-text",),
        ],
        style={'text-align': 'center'}

    ),
    html.Div(
        [
            dbc.Button("View Current Job Assignments Report", color="light", id="current_btn", n_clicks=0),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Current Job Assignments Report")),
                    dbc.ModalBody(
                        "This will contain the table for current assignments.", 
                        id='currentassign_list'
                    ),
                ],
                id="current_modal",
                size="xl",
                is_open=False,
            ),
        ],
        className="d-grid gap-2",
    )
]
future_assignments = [
    dbc.CardBody(
        [
            html.H2("Card title", className="card-title", id='future_job_asn'),
            # html.P("This is some card content that we'll reuse", className="card-text",),
        ],
        style={'text-align': 'center'}
    ),
    html.Div(
        [
            dbc.Button("View Future Job Assignments Report", color="light", id="future_btn", n_clicks=0),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Future Job Assignments Report")),
                    dbc.ModalBody(
                        "This will contain the table for future assignments.", 
                        id='futureassign_list'
                    ),
                ],
                id="future_modal",
                size="xl",
                is_open=False,
            ),
        ],
        className="d-grid gap-2",
    )
]

layout = html.Div(
    [
        html.H2("Jobs"),
        html.Hr(),
        #CARDS
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(job_openings, color="dark", outline=True) #outline=True
                ),
                dbc.Col(
                    dbc.Card(current_assignments, color="dark", outline=True)
                ),
                dbc.Col(
                    dbc.Card(future_assignments, color="dark", outline=True)
                ),
            ]
        ),
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        type="text", id="job_name_filter", placeholder="🔍 Search Job"
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.RadioItems(
                        id="status_filter",
                        options=[
                            {"label": "All", "value": "All"},
                            {"label": "Hiring", "value": "Hiring"},
                            {"label": "Not Hiring", "value": "Not Hiring"},
                        ],
                        value="All",
                        inline=True
                    ),
                )
            ]
        ),
        html.Br(),
        html.Br(),
        html.Div(
                "This will contain the table for all jobs.",
                id='job_list'
        ),
        html.Br(),
        # ADD NEW JOB BUTTON
        html.Div(
            [
                dbc.Button("Add New Job", id="new_job", n_clicks=0, color= 'warning', href='/jobs/jobprofile?mode=add'),
            ]
        ),
        html.Br(),
    ]
)

@app.callback(
    [
        Output('job_list','children'),
        Output('currentopen_list', 'children'),
        Output('currentassign_list', 'children'),
        Output('futureassign_list', 'children'),
        Output('current_job_open', 'children'),
        Output('current_job_asn', 'children'),
        Output('future_job_asn', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('job_name_filter', 'value'),
        Input('status_filter', 'value')
    ]
)

def loadjoblist (pathname, searchjob, searchstatus):
    if pathname == '/jobs':

        # QUERY JOB OPENING STATS----------------------------------------------------------------------
        sql_jobopen = """
        SELECT COUNT(*)
            FROM jobs
            WHERE job_s = 'Hiring'
                AND jobs.job_delete_ind = false
        """
        values_jobopen = []
        colnames_jobopen = ['stat']
        jobopen_query = db.querydatafromdatabase(sql_jobopen, values_jobopen, colnames_jobopen)
        
        if jobopen_query.shape[0]:
            jobopen_stats = jobopen_query['stat'][0]
        else:
            jobopen_stats = "0"
        
        jobopen_card = f'📂 {jobopen_stats} Jobs Currently Hiring'

        # QUERY CURRENT ASSIGNMENTS STATS----------------------------------------------------------------------
        sql_currentasn = """
        SELECT COUNT(*)
            FROM assignments
            WHERE asn_sd <= CURRENT_DATE
                AND CURRENT_DATE < asn_ed
                AND assignment_delete_ind = false
        """
        values_currentasn = []
        colnames_currentasn = ['stat']
        currentasn_query = db.querydatafromdatabase(sql_currentasn, values_currentasn, colnames_currentasn)

        if currentasn_query.shape[0]:
            currentasn_stats = currentasn_query['stat'][0]
        else:
            currentasn_stats = "0"
        
        currentasn_card = f'💻 {currentasn_stats} Jobs Filled and Ongoing'

        # QUERY FUTURE ASSIGNMENTS STATS----------------------------------------------------------------------
        sql_futureasn = """
        SELECT COUNT(*)
            FROM assignments
            WHERE CURRENT_DATE < asn_sd
                AND assignment_delete_ind = false
        """
        values_futureasn = []
        colnames_futureasn = ['stat']
        futureasn_query = db.querydatafromdatabase(sql_futureasn, values_futureasn, colnames_futureasn)

        if futureasn_query.shape[0]:
            futureasn_stats = futureasn_query['stat'][0]
        else:
            futureasn_stats = "0"
        
        futureasn_card = f'📈 {futureasn_stats} Upcoming Assignments'

        # QUERY JOB LIST----------------------------------------------------------------------
        sql ="""
        SELECT job_n, dept, job_s, job_id
	    FROM jobs
        WHERE job_delete_ind = false
        """
        values = []
        colnames = ['Job Name','Job Department','Status','ID']

        # BEFORE ADDING QUERY IN PGADMIN, ADD FILTER
        if searchjob:
            # We use the operator ILIKE for pattern-matching
            sql += "AND job_n ILIKE %s"
            values += [f"%{searchjob}%"]

        if searchstatus == 'Hiring' or searchstatus == 'Not Hiring':
            sql += f" AND job_s = '{searchstatus}'"
        else:
            pass

        # RUN MODIFY DB FORMULA
        joblist = db.querydatafromdatabase(sql, values, colnames)

        # IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if joblist.shape[0]:
            
            #CREATE EDIT/DELETE BUTTONS COLUMN
            editbuttons =[]
            for job_id in joblist['ID']:
                editbuttons += [
                    dbc.Button(
                        '⚙️ Edit or Remove', 
                        href=f"/jobs/jobprofile?mode=edit&id={job_id}",
                        size='sm',
                        color='dark'
                    )
                ]
            
            #ADD BUTTONS TO joblist TABLE
            # joblist['Employee List'] = assignmentbtn
            joblist['Action'] = editbuttons
            #REMOVE ID COLUMN -> axis options: 1 - column, 0 - row
            joblist.drop('ID', axis=1, inplace=True) 

            job_table = html.Div(
                dbc.Table.from_dataframe(
                    joblist, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )
        # IF EMPTY, RAISE PROMPT
        else:
            job_table = "No records to display"
        
        # QUERY CURRENT JOB OPENINGS----------------------------------------------------------------
        sql_opening ="""
 		SELECT job_n, STRING_AGG(skills.sk_n,', '), job_od
            FROM jobs
            FULL OUTER JOIN job_skill ON job_skill.job_id = jobs.job_id
            FULL OUTER JOIN skills ON skills.sk_id = job_skill.sk_id
            WHERE job_s = 'Hiring'
                AND job_delete_ind = false
			GROUP BY job_n, job_od
        """
        values_opening = []
        colnames_opening = ['Job Name','Skill Requirements','Opening Date']
        openinglist = db.querydatafromdatabase(sql_opening, values_opening, colnames_opening)

        # IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if openinglist.shape[0]:
            jobopening_table = html.Div(
                dbc.Table.from_dataframe(
                    openinglist, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )
        # IF EMPTY, RAISE PROMPT
        else:
            jobopening_table = "No records to display", 
        
        # QUERY CURRENT JOB ASSIGNMENTS----------------------------------------------------------------
        sql_current ="""
        SELECT jobs.job_n, CONCAT(employees.emp_fn,' ',employees.emp_ln), asn_sd, asn_ed
            FROM assignments
            INNER JOIN jobs ON jobs.job_id = assignments.job_id
            INNER JOIN employees ON employees.emp_id = assignments.emp_id
            WHERE asn_sd < CURRENT_DATE
                AND CURRENT_DATE < asn_ed
                AND assignment_delete_ind = false
        """
        values_current = []
        colnames_current = ['Job Name','Employee','Start Date','End Date']
        currentasnlist = db.querydatafromdatabase(sql_current, values_current, colnames_current)

        # IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if currentasnlist.shape[0]:
            currentasn_table = html.Div(
                dbc.Table.from_dataframe(
                    currentasnlist, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )
        # IF EMPTY, RAISE PROMPT
        else:
            currentasn_table = "No records to display", 

        # QUERY FUTURE JOB ASSIGNMENTS----------------------------------------------------------------
        sql_future ="""
        SELECT jobs.job_n, CONCAT(employees.emp_fn,' ',employees.emp_ln), asn_sd, asn_ed
            FROM assignments
            INNER JOIN jobs ON jobs.job_id = assignments.job_id
            INNER JOIN employees ON employees.emp_id = assignments.emp_id
            WHERE CURRENT_DATE < asn_sd
                AND assignment_delete_ind = false
        """
        values_future = []
        colnames_future = ['Job Name','Employee','Start Date','End Date']
        futureasnlist = db.querydatafromdatabase(sql_future, values_future, colnames_future)

        # IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if futureasnlist.shape[0]:
            futureasn_table = html.Div(
                dbc.Table.from_dataframe(
                    futureasnlist, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )
        # IF EMPTY, RAISE PROMPT
        else:
            futureasn_table = "No records to display", 
    
    else:
        raise PreventUpdate
    
    return [job_table, jobopening_table, currentasn_table, futureasn_table, jobopen_card, currentasn_card, futureasn_card]

# OPEN REPORTS
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

app.callback(
    Output("opening_modal", "is_open"),
    Input("opening_btn", "n_clicks"),
    State("opening_modal", "is_open"),
)(toggle_modal)
app.callback(
    Output("current_modal", "is_open"),
    Input("current_btn", "n_clicks"),
    State("current_modal", "is_open"),
)(toggle_modal)
app.callback(
    Output("future_modal", "is_open"),
    Input("future_btn", "n_clicks"),
    State("future_modal", "is_open")
)(toggle_modal)