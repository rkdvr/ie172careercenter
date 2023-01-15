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
from apps.employees import add_empjob
from apps.jobs import add_jobskill

layout = html.Div(
    [
        html.Div( # This div shall contain all dcc.Store objects
            [
                dcc.Store(id='jobprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Job Information"),
        html.Hr(),
        #Job Name----------------------------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Job Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="jobprof_name", placeholder="Enter job name"
                    ),
                    width=4,
                ),
            ],
            className="mb-3",
        ),
        #Job Description----------------------------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Description", width=2),
                dbc.Col(
                    dbc.Textarea(className="mb-3", placeholder="Enter description here", id="jobprof_desc"),
                    width=4
                )
            ],
            className="mb-3",
        ),
        #Job Tasks----------------------------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Tasks", width=2),
                dbc.Col(
                    dbc.Textarea(className="mb-3", placeholder="Enter tasks here", id="jobprof_tasks"),
                    width=4
                )
            ],
            className="mb-3",
        ),
        #Job Department----------------------------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Department", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="jobprof_dept", placeholder="Enter job department"
                    ),
                    width=4,
                ),
            ],
            className="mb-3" 
        ),
        #Job Opening Date----------------------------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Opening Date", width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                            id='jobprof_od',
                    ),
                    width=4,
                ),
            ],
            className="mb-3",
        ),
        html.Br(),
        #Job Status----------------------------------------------------------------------
        dbc.Row(           
            [
                dbc.Label("Status", width=2),
                dbc.Col(
                    html.Div(
                        [
                            dbc.RadioItems(
                                options=[
                                    {"label": "Hiring", "value": "Hiring"},
                                    {"label": "Not Hiring", "value": "Not Hiring"},
                                ],
                                value="Hiring",
                                id="jobprof_status",
                                inline=True,
                            ),
                        ]
                    )
                ),
            ],
            className="mb-3",
        ),
        html.Div(
            [
                #SKILLS LIST----------------------------------------------------------------------
                html.H4('Skills Required'),
                dbc.Row(
                    "Insert table of skills here.",
                    id = "job_skills"
                ),
                html.Br(),
                html.Div(
                    [
                        dbc.Button("Add Skill Requirement", id="add_job_skill", n_clicks=0, color= 'secondary'),
                    ]
                ), 
                html.Br(),
                #EMPLOYEE LIST----------------------------------------------------------------------
                html.H4('Record of Assigned Employees'),
                dbc.Row(
                    "Insert table of employees here.",
                    id = "job_emplist"
                ),
                html.Br(),
                html.Div(
                    [
                        dbc.Button("Add Employee to Records", id="add_job_emp", n_clicks=0, color= 'secondary'),
                    ]
                ), 
                html.Br(),
                #DELETE----------------------------------------------------------------------
                dbc.Row(           
                    [
                        dbc.Label("Delete Job?", width=2, style={'color': 'red'}),
                        dbc.Col(
                            dbc.Checklist(
                                id='job_removerecord',
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
            id='job_editelements_div'
        ),
        #SUBMIT----------------------------------------------------------------------
        dbc.Button("Submit", color= 'warning', id='jobprof_submitbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader("New Job Added!"),
                dbc.ModalBody('temp message', id='jobprof_feedback'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="jobprof_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                    )
                ),
            ],
            id="jobprof_modal",
            is_open=False,
        )  
    ]
)

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("jobprof_modal", "is_open"),
        Output("jobprof_feedback", "children"),
        Output("jobprof_closebtn", "href")
    ],
    [
        Input("jobprof_submitbtn", "n_clicks"),
        Input("jobprof_closebtn", "n_clicks"),
    ],
    [
        State('jobprof_name', 'value'),
        State('jobprof_desc', 'value'),
        State('jobprof_tasks', 'value'),
        State('jobprof_dept', 'value'),
        State('jobprof_od', 'date'),
        State('jobprof_status', 'value'),
        State('url', 'search'),
        State('job_removerecord', 'value'),
    ]
)
def empprof_submitprocess(submitbtn, closebtn,
                        jobname, jobdesc, jobtasks, jobdept, jobopendate, jobstatus,
                        search, jobremove): 

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
    if eventid == 'jobprof_submitbtn' and submitbtn:
        
        # OPEN MODAL
        openmodal = True

        inputs = [
            jobname, 
            jobdesc,
            jobtasks,
            jobdept,
            jobopendate,
            jobstatus
        ] 

        # IF INVALID INPUTS,
        if not all(inputs):
            # GIVE ERROR PROMPT
            feedbackmsg = "Please provide all inputs correctly."
        elif len(jobtasks) > 1024:
            # GIVE ERROR PROMPT
            feedbackmsg = "Task description is too long for this job."

        # ELIF VALID INPUTS
        else:
            # REF OKAY BUTTON TO JOB HOME
            okay_href = '/jobs'

            parsed = urlparse(search)
            mode = parse_qs(parsed.query)['mode'][0]

            # IF MODE IS ADD
            if mode == 'add':
                # SAVE TO DB
                sqlcode = """
                INSERT INTO jobs(job_n,job_ds,job_t,dept,job_od,job_s)
                VALUES(%s, %s, %s, %s, %s, %s)
                """
                values = [jobname, jobdesc,jobtasks,jobdept, jobopendate,jobstatus] 
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Job Added!"

            # ELIF MODE IS EDIT
            elif mode == 'edit':
                job_id = parse_qs(parsed.query)['id'][0]

                # UPDATE DB QUERY
                sqlcode = """
                UPDATE jobs
                SET
                job_n = %s,
                job_ds = %s,
                job_t = %s,
                dept = %s,
                job_od = %s,
                job_s = %s,
                job_delete_ind = %s
                WHERE job_id = %s
                """
                
                to_delete = bool(jobremove)
                
                values = [jobname, jobdesc,jobtasks,jobdept,jobopendate,jobstatus,to_delete, job_id]
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "Job has been updated!"
            else:
                raise PreventUpdate #can be a custom URL ERROR MESSAGE

    # ELIF CLOSE BUTTON WAS CLICKED,
    elif eventid == 'jobprof_closebtn' and closebtn:
        # CLOSE MODAL
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]

# lOAD ELEMENTS UPON PAGE LOAD--------------------------------------------------------------------------------
@app.callback(
    [
        Output('jobprof_toload', 'data'),
        Output('job_editelements_div', 'style'),
        Output("add_job_skill", "href"),   
        Output("add_job_emp", "href"),
        Output('job_skills', 'children'),
        Output('job_emplist', 'children'),  
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def triggereditmode (pathname, search):

    if pathname == '/jobs/jobprofile':

        parsed = urlparse(search)
        mode = parse_qs(parsed.query)['mode'][0] 
        to_load = 1 if mode == 'edit' else 0
        editelementsdiv = {'display': 'none'} if not to_load else None

        #EMPTY VALUES IF ADD MODE
        jobskill_href = ""
        empjob_href = ""
        jobskilltable = ""
        assignment_table = "" 

        # VALUES IF EDIT MODE
        if to_load:
            parsed = urlparse(search)
            job_id = parse_qs(parsed.query)['id'][0]
            # ADD REFERENCE TO FORMS TO ADD TO JUNCTION TABLES
            jobskill_href = f"/jobs/jobprofile/jobskillprofile?mode=add&id={job_id}"
            empjob_href = f"/jobs/jobprofile/assignmentprofile?mode=add&id={job_id}"

            # LOAD JOB-SKILL CHILDREN--------------------------------------------------------
            sql_jobsk = """
            SELECT skills.sk_n, job_skill.sk_l, concat(job_skill.job_id, job_skill.sk_id)
                FROM jobs
                INNER JOIN job_skill on job_skill.job_id = jobs.job_id
                INNER JOIN skills on skills.sk_id = job_skill.sk_id
            WHERE jobs.job_id = %s
                AND jobs.job_delete_ind = false
                AND job_skill.job_skill_delete_ind = false
                AND skills.skill_delete_ind = false
            """
            values_jobsk = [job_id]
            colnames_jobsk = ['Skill', 'Level', 'ID']
            job_skills_df = db.querydatafromdatabase(sql_jobsk, values_jobsk, colnames_jobsk)

            if job_skills_df.shape[0]:
                # ADD A BUTTON PER ROW THAT CAN EDIT ITS CONTENTS
                buttons =[]
                for jobsk_id in job_skills_df['ID']:
                    buttons += [
                        dbc.Button(
                            '⚙️ Edit or Remove', 
                            href=f"/jobs/jobprofile/jobskillprofile?mode=edit&id={jobsk_id}",
                            size='sm',
                            color='dark'
                        )
                    ]
                
                # ADD COLUMN FOR EDIT BUTTONS
                job_skills_df['Action'] = buttons #add column named action containing the buttons
                job_skills_df.drop('ID', axis=1, inplace=True) #remove id col -> axis: 1 - column, 0 - row

                # LOAD TABLES
                jobskilltable = html.Div(
                    dbc.Table.from_dataframe(
                        job_skills_df, 
                        striped=True, 
                        bordered=True, 
                        hover=True, 
                        size='sm',
                        style={'text-align': 'center'}
                    )
                )
            else:
                # RAISE NULL PROMPT
                jobskilltable = "No records to display"
            
            # LOAD ASSIGNMENT CHILDREN--------------------------------------------------------
            sql_assignment = """
            SELECT concat(emp_fn, ' ',emp_ln), asn_sd, asn_ed, asn_id
                FROM employees
                INNER JOIN assignments on assignments.emp_id = employees.emp_id
                INNER JOIN jobs on jobs.job_id = assignments.job_id
            WHERE jobs.job_id = %s
                AND assignment_delete_ind = False 
				AND job_delete_ind = False
            """
            values_assignment = [job_id]
            colnames_assignment = ['Job Name', 'Start Date', 'End Date', 'ID']
            assignmentdf = db.querydatafromdatabase(sql_assignment, values_assignment, colnames_assignment)

            if assignmentdf.shape[0]:
                # ADD A BUTTON PER ROW THAT CAN EDIT ITS CONTENTS
                buttons =[]
                for asn_id in assignmentdf['ID']:
                    buttons += [
                        dbc.Button(
                            '⚙️ Edit or Remove', 
                            href=f"/jobs/jobprofile/assignmentprofile?mode=edit&id={asn_id}",
                            size='sm',
                            color='dark'
                        )
                    ]
                
                # ADD COLUMN FOR EDIT BUTTONS
                assignmentdf['Action'] = buttons #add column named action containing the buttons
                assignmentdf.drop('ID', axis=1, inplace=True) #remove id col -> axis: 1 - column, 0 - row

                # LOAD TABLES
                assignment_table = html.Div(
                    dbc.Table.from_dataframe(
                        assignmentdf, 
                        striped=True, 
                        bordered=True, 
                        hover=True, 
                        size='sm',
                        style={'text-align': 'center'}
                    )
                )
            else:
                # RAISE NULL PROMPT
                assignment_table = "No records to display"
            
    else:
        raise PreventUpdate

    return [to_load, editelementsdiv, jobskill_href, empjob_href, jobskilltable, assignment_table]

#LOAD INFORMATION TO INTERFACE BASED ON MODE--------------------------------------------------------------------------------
@app.callback(
    [
        Output('jobprof_name', 'value'),
        Output('jobprof_desc', 'value'),
        Output('jobprof_tasks', 'value'),
        Output('jobprof_dept', 'value'),
        Output('jobprof_od', 'date'),
        Output('jobprof_status', 'value'),
    ],
    [
        Input('jobprof_toload', 'modified_timestamp')
    ],
    [
        State('jobprof_toload', 'data'),
        State('url', 'search')
    ]
)
def loadjobinfo(timestamp, to_load, search):
    
    #IF TO_LOAD IS 1 (MODE IS EDIT)
        # lOAD BASIC INFO
        # QUERY JUNCTION TABLES
        # FOR EACH TABLE THAT HAS VALUES
            # ADD A BUTTON PER ROW THAT CAN EDIT ITS CONTENTS
            # ADD COLUMN FOR EDIT BUTTONS
            # LOAD TABLES
        # ELIF NO VALUE
            # RAISE NULL PROMPT
    # ELSE, PREVENT UDPATE

    if to_load == 1:
        parsed = urlparse(search)
        job_id = parse_qs(parsed.query)['id'][0] #the key is 'id' in URL

        # LOAD OB INFORMATION-----------------------------------------------------------------------
        #1 query job information from DB
        sql = """
        SELECT job_n,job_ds,job_t,dept,job_od,job_s
        FROM jobs
        WHERE job_id = %s
        """
        values =[job_id]
        colnames =['jobname', 'jobdesc', 'jobtasks', 'jobdept', 'jobopendate', 'jobstatus']
        df = db.querydatafromdatabase(sql, values, colnames) #df = dataframe

        #2 load on interface
        jobname = df['jobname'][0]
        jobdesc = df['jobdesc'][0]
        jobtasks = df['jobtasks'][0]
        jobdept = df['jobdept'][0]
        jobopendate = df['jobopendate'][0]
        jobstatus = df['jobstatus'][0]

        return [jobname, jobdesc, jobtasks, jobdept, jobopendate, jobstatus]

    else:
        raise PreventUpdate