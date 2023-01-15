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

layout = html.Div(
    [
        html.Div( # This div shall contain all dcc.Store objects
            [
                dcc.Store(id='jobskill_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Job Skill Records"),
        html.Hr(),
        #JOB NAME
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Job Name", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='job_skdropdown',
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
        #SKILL
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Skill", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='skill_jdropdown',
                                placeholder = 'Select Skill',
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
            id='skill_jdropdown_div'
        ),
        #SKILL LEVEL
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Skill Level", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='level_jskdropdown',
                                options=[
                                    {'label':'1', 'value':'1'},
                                    {'label':'2', 'value':'2'},
                                    {'label':'3', 'value':'3'},
                                    {'label':'4', 'value':'4'},
                                    {'label':'5', 'value':'5'},
                                    {'label':'6', 'value':'6'},
                                ],
                                placeholder = 'Select from level 1 to 5',
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
            id='level_dropdown_div'
        ),
        html.Br(),
        #DELETE
        html.Div(
            [
                dbc.Row(           
                    [
                        dbc.Label("Remove Job Skill Record?", width=2, style={'color': 'red'}),
                        dbc.Col(
                            dbc.Checklist(
                                id='jobskill_remove',
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
            id='jobskill_remove_div',
        ),
        #SUBMIT
        dbc.Button("Submit", color= 'warning', id='jobskill_submitbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody('temp message', id='jobskill_feedbackmsg'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="jobskill_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                    )
                ),
            ],
            id="jobskill_modal",
            is_open=False,
        ),
        html.Br(),
        html.Br(),
        html.Div(
            dbc.Card(
                [
                    dbc.CardHeader('DISCLAIMER'),
                    dbc.CardBody(
                        [
                            html.P('Dropdown is empty if data is still unavailable or if all items were already previously assigned.'),
                            html.P('Please contact your website moderator if a record was mistakenly deleted or needs to be retrieved.'),
                        ]
                    )
                ],
                color='dark',
                outline=True,
                className="w-50",
            ),
            id='jobskill_disclaimer'
        )
    ]
)


#lOAD ELEMENTS UPON PAGE LOAD-------------------------------------------------------------------------------
@app.callback(
    [
        Output('jobskill_toload', 'data'),
        Output('jobskill_remove_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def loadpageelements(pathname, search):

    if pathname == '/jobs/jobprofile/jobskillprofile':

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None

    else:
        raise PreventUpdate

    return [to_load, removediv_style]

#LOAD DB TO INTERFACE BASED ON MODE-------------------------------------------------------------------------------
@app.callback(
    [
        Output('job_skdropdown', 'value'),
        Output('skill_jdropdown', 'value'),
        Output('level_jskdropdown', 'value'),
        Output('job_skdropdown', 'options'),
        Output('skill_jdropdown', 'options'),
        Output('job_skdropdown', 'disabled'),
        Output('skill_jdropdown', 'disabled'),
    ],
    [
        Input('jobskill_toload', 'modified_timestamp'),
    ],
    [
        State('jobskill_toload', 'data'),
        State('url', 'search'),
        State('url', 'pathname')
    ]
)
def loadjobskillinfo (timestamp, jobskill_to_load, search, pathname):
    
    #IF PAGE IS IN EDIT MODE, LOAD ALL VALUES, REGARDLESS OF ORIGIN PAGE
    parsed = urlparse(search)
    
    # INITIALIZE SQL QUERIES
    sql_restrictjob = ""
    values_restrictjob = []
    cols_restrictjob = ['label', 'value']

    sql_restrictskill = ""
    values_restrictskill = []
    cols_restrictskill = ['label', 'value']
    
    skill_options = []

    #GETTING NECESSARY IDS
    #IF PAGE IS IN EDIT MODE,
    if jobskill_to_load:
        jobskill_id = parse_qs(parsed.query)['id'][0]

        job_disabled = True
        skill_disabled = True

        #QUERY JOB-SKILL INFO
        sql_jobskillinfo = """
        SELECT public.job_skill.job_id, public.job_skill.sk_id, public.job_skill.sk_l
            FROM public.job_skill
            INNER JOIN skills on public.job_skill.sk_id = skills.sk_id
            INNER JOIN jobs on public.job_skill.job_id = jobs.job_id
        WHERE concat(public.job_skill.job_id, public.job_skill.sk_id) = %s
        """
        values_jobskillinfo = [f'{jobskill_id}']
        col_jobskillinfo = ['job_id','sk_id', 'sk_l']
        jobskillinfo_table = db.querydatafromdatabase(sql_jobskillinfo, values_jobskillinfo, col_jobskillinfo)
        job_id = int(jobskillinfo_table['job_id'][0])
        skill_id = int(jobskillinfo_table['sk_id'][0])
        level = int(jobskillinfo_table['sk_l'][0])

        # LOAD VALUE OF CURRENT ENTRY
        sql_restrictjob += """
        (SELECT job_n as label, job_id as value
            FROM jobs
            WHERE job_id = %s)
        UNION
        """
        values_restrictjob += [job_id]

        sql_restrictskill += """
        (SELECT sk_n as label, sk_id as value
            FROM skills
            WHERE sk_id = %s)
        UNION
        """
        values_restrictskill += [skill_id]

    #ELIF PAGE IS IN ADD MODE,
    elif jobskill_to_load == 0:
        loadedID = parse_qs(parsed.query)['id'][0]
        level = None

        #IF ORIGIN PAGE IS JOB PROFILE
        if pathname == '/jobs/jobprofile/jobskillprofile':
            #lOAD JOB ID
            job_id = loadedID
            skill_id = None
            job_disabled = True
            skill_disabled = False
        
        #ELIF ORIGIN PAGE IS SKILL PROFILE
        elif pathname == '/skills/skillprofile/jobskillprofile':
            #LOAD SKILL ID
            job_id = None
            skill_id = loadedID
            job_disabled = False
            skill_disabled = True
    
    else:
        raise PreventUpdate
            
    # AFTER RETRIEVING THE NECESSARY IDS, LOAD RESTRICTED DROPDOWN VALUES
    #Restrict values of job dropdown
    sql_restrictjob += """
    (SELECT job_n as label, job_id as value
        FROM jobs
        WHERE jobs.job_delete_ind = FALSE
    EXCEPT SELECT job_n, job_skill.job_id
        FROM job_skill
        INNER JOIN jobs ON jobs.job_id = job_skill.job_id
        WHERE job_skill.sk_id = %s)
    """
    values_restrictjob += [skill_id]
    jobrestricted = db.querydatafromdatabase(sql_restrictjob, values_restrictjob, cols_restrictjob)
    job_options = jobrestricted.to_dict('records')
    
    #Restrict values of skill dropdown
    sql_restrictskill += """
    (SELECT sk_n as label, sk_id as value
        FROM skills
        WHERE skills.skill_delete_ind = false
    EXCEPT SELECT sk_n, job_skill.sk_id
        FROM job_skill
        INNER JOIN skills ON skills.sk_id = job_skill.sk_id
        WHERE job_skill.job_id = %s)
    """
    values_restrictskill += [job_id]
    skillrestricted = db.querydatafromdatabase(sql_restrictskill, values_restrictskill, cols_restrictskill)
    skill_options = skillrestricted.to_dict('records')

    return [job_id, skill_id, level, job_options, skill_options, job_disabled, skill_disabled]

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("jobskill_modal", "is_open"),
        Output("jobskill_feedbackmsg", "children"),
        Output("jobskill_closebtn", "href")
    ],
    [
        Input("jobskill_submitbtn", "n_clicks"),
        Input("jobskill_closebtn", "n_clicks"),
    ],
    [
        State('job_skdropdown', 'value'),
        State('skill_jdropdown', 'value'),
        State('level_jskdropdown', 'value'),
        State('url', 'search'),
        State('url', 'pathname'), #NEW
        State('jobskill_remove', 'value')
    ]
)
def jobskill_submitprocess(submitbtn, closebtn, 
                        jobdropdown, skilldropdown,level,
                        search, pathname, jobskill_remove):

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
    if eventid == 'jobskill_submitbtn' and submitbtn:
        # OPEN MODAL
        openmodal = True

        inputs = [
            jobdropdown,
            skilldropdown,
            level
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
                # IF ORIGIN PAGE IS JOBPROF
                if pathname == '/jobs/jobprofile/jobskillprofile':
                    # REF OKAY BUTTON TO JOBPROF
                    okay_href = f'/jobs/jobprofile?mode=edit&id={returnid}'
                # ELIF ORIGIN PAGE IS SKILLPROF
                elif pathname == '/skills/skillprofile/jobskillprofile':
                    # REF OKAY BUTTON TO SKILLPROF
                    okay_href = f'/skills/skillprofile?mode=edit&id={returnid}'

                # SAVE TO DB
                sqlcode = """
                INSERT INTO public.job_skill(JOB_ID,SK_ID, SK_L)
                VALUES(%s,%s,%s)
                """
                values = [jobdropdown, skilldropdown,level]
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Skill requirement recorded to job!"

            # ELIF MODE IS EDIT
            elif mode == 'edit':
                # UPDATE DB QUERY
                jobskill_id = parse_qs(parsed.query)['id'][0]

                sqlcode = """
                UPDATE public.job_skill
                SET
                job_id = %s,
                sk_id = %s,
				sk_l = %s,
                job_skill_delete_ind = %s
                WHERE concat(public.job_skill.job_id,public.job_skill.sk_id) = %s
                """
                to_delete = bool(jobskill_remove) #checking asn_remove value (either true or false)
                values = [jobdropdown, skilldropdown, level, to_delete, f'{jobskill_id}']
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "Job's skill requirement updated!"

                # QUERY JOBID AND JOBID FROM ASNID
                sql_returnid = """
                SELECT job_id, sk_id
                FROM public.job_skill
                WHERE concat(public.job_skill.job_id,public.job_skill.sk_id) = %s
                """
                values_returnid = [f'{jobskill_id}']
                cols_returnid = ['job_id', 'sk_id']
                returnidvalue = db.querydatafromdatabase(sql_returnid, values_returnid, cols_returnid)
                job_id = int(returnidvalue['job_id'][0])
                sk_id = int(returnidvalue['sk_id'][0])

                # IF ORIGIN PAGE IS JOBPROF
                if pathname == '/jobs/jobprofile/jobskillprofile':
                    # REF OKAY BUTTON TO JOBPROF
                    okay_href = f'/jobs/jobprofile?mode=edit&id={job_id}'
                # ELIF ORIGIN PAGE IS SKILLPROF
                elif pathname == '/skills/skillprofile/jobskillprofile':
                    # REF OKAY BUTTON TO SKILLPROF
                    okay_href = f'/skills/skillprofile?mode=edit&id={sk_id}'

            else:
                raise PreventUpdate #can be a custom url error message
            
    elif eventid == 'jobskill_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]
