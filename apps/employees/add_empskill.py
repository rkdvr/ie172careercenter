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
                dcc.Store(id='empskill_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Employee Skill Records"),
        html.Hr(),
        #EMPLOYEE NAME
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Employee Name", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='emp_skdropdown',
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
            id='emp_skdropdown_div'
        ),
        #SKILL
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Skill", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='skill_dropdown',
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
            id='skill_dropdown_div'
        ),
        #SKILL LEVEL
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Skill Level", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='level_skdropdown',
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
                        dbc.Label("Remove Employee Skill Record?", width=2, style={'color': 'red'}),
                        dbc.Col(
                            dbc.Checklist(
                                id='empskill_remove',
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
            id='empskill_remove_div',
        ),
        #SUBMIT
        dbc.Button("Submit", color= 'warning', id='empskill_submitbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody('temp message', id='empskill_feedbackmsg'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="empskill_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                    )
                ),
            ],
            id="empskill_modal",
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
            id='empskill_disclaimer'
        )
    ]
)

#lOAD ELEMENTS UPON PAGE LOAD-------------------------------------------------------------------------------
@app.callback(
    [
        Output('empskill_toload', 'data'),
        Output('empskill_remove_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def loadpageelements(pathname, search):

    if pathname == '/employees/employeeprofile/skillrecord':

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
        Output('emp_skdropdown', 'value'),
        Output('skill_dropdown', 'value'),
        Output('level_skdropdown', 'value'),
        Output('emp_skdropdown', 'options'),
        Output('skill_dropdown', 'options'),
        Output('emp_skdropdown', 'disabled'),
        Output('skill_dropdown', 'disabled'),
    ],
    [
        Input('empskill_toload', 'modified_timestamp'),
    ],
    [
        State('empskill_toload', 'data'),
        State('url', 'search'),
        State('url', 'pathname')
    ]
)
def loadparticipationinfo (timestamp1,empskill_to_load, search, pathname):
    
    #LOADING VALUES AND OPTIONS---------------
    parsed = urlparse(search)

    # INITIALIZE SQL QUERIES
    sql_restrictemp = ""
    values_restrictemp = []
    cols_restrictemp = ['label', 'value']

    sql_restrictskill = ""
    values_restrictskill = []
    cols_restrictskill = ['label', 'value']
    
    # skill_options = []

    #GETTING NECESSARY IDS
    #IF PAGE IS IN EDIT MODE,
    if empskill_to_load:
        empskill_id = parse_qs(parsed.query)['id'][0]

        employee_disabled = True
        skill_disabled = True

        #GET IDS FROM JUNCTION ID
        sql_empskillinfo = """
        SELECT public.employee_skill.emp_id, public.employee_skill.sk_id, public.employee_skill.sk_l
            FROM public.employee_skill
            INNER JOIN skills on public.employee_skill.sk_id = skills.sk_id
            INNER JOIN employees on public.employee_skill.emp_id = employees.emp_id
        WHERE concat(public.employee_skill.emp_id, public.employee_skill.sk_id) = %s
        """
        values_empskillinfo = [f'{empskill_id}']
        col_empskillinfo = ['emp_id', 'sk_id', 'sk_l']
        empskillinfo_table = db.querydatafromdatabase(sql_empskillinfo, values_empskillinfo, col_empskillinfo)
        employee_id = int(empskillinfo_table['emp_id'][0])
        skill_id = int(empskillinfo_table['sk_id'][0])
        level = int(empskillinfo_table['sk_l'][0])

        # LOAD VALUE OF CURRENT ENTRY
        sql_restrictemp += """
        (SELECT CONCAT(emp_fn,' ',emp_ln) as label, emp_id as value
            FROM employees
            WHERE emp_id = %s)
        UNION
        """
        values_restrictemp += [employee_id]

        sql_restrictskill += """
        (SELECT sk_n as label, sk_id as value
            FROM skills
            WHERE sk_id = %s)
        UNION
        """
        values_restrictskill += [skill_id]

    #ELIF PAGE IS IN ADD MODE,
    elif empskill_to_load == 0:        
        loaded_ID = parse_qs(parsed.query)['id'][0]
        level = None

        #IF ORIGIN PAGE IS EMPLOYEE PROFILE
        if pathname == '/employees/employeeprofile/skillrecord':
            #lOAD EMP ID
            employee_id = loaded_ID
            skill_id = None
            employee_disabled = True
            skill_disabled = False
       
        #ELIF ORIGIN PAGE IS SKILL PROFILE
        elif pathname == '/skills/skillprofile/skillrecord':           
            #EMPTY EMPLOYEE
            employee_id = None
            skill_id = loaded_ID
            employee_disabled = False
            skill_disabled = True

    else:
        raise PreventUpdate
        
    # AFTER RETRIEVING THE NECESSARY IDS, LOAD RESTRICTED DROPDOWN VALUES
    #Restrict values of employee dropdown
    sql_restrictemp += """
    (SELECT CONCAT(emp_fn,' ',emp_ln) as label, emp_id as value
        FROM employees
        WHERE employees.employee_delete_ind = FALSE
    EXCEPT SELECT CONCAT(emp_fn,' ',emp_ln), employee_skill.emp_id
        FROM employee_skill
        INNER JOIN employees ON employees.emp_id = employee_skill.emp_id
        WHERE employee_skill.sk_id = %s)
    """
    values_restrictemp += [skill_id]
    employeerestricted = db.querydatafromdatabase(sql_restrictemp, values_restrictemp, cols_restrictemp)
    employee_options = employeerestricted.to_dict('records')
    
    #Restrict values of skill dropdown
    sql_restrictskill += """
    (SELECT sk_n as label, sk_id as value
        FROM skills
        WHERE skills.skill_delete_ind = false
    EXCEPT SELECT sk_n, employee_skill.sk_id
        FROM employee_skill
        INNER JOIN skills ON skills.sk_id = employee_skill.sk_id
        WHERE employee_skill.emp_id = %s)
    """
    values_restrictskill += [employee_id]
    skillrestricted = db.querydatafromdatabase(sql_restrictskill, values_restrictskill, cols_restrictskill)
    skill_options = skillrestricted.to_dict('records')

    

    return [employee_id, skill_id, level, employee_options, skill_options, employee_disabled, skill_disabled]

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("empskill_modal", "is_open"),
        Output("empskill_feedbackmsg", "children"),
        Output("empskill_closebtn", "href")
    ],
    [
        Input("empskill_submitbtn", "n_clicks"),
        Input("empskill_closebtn", "n_clicks"),
    ],
    [
        State('emp_skdropdown', 'value'),
        State('skill_dropdown', 'value'),
        State('level_skdropdown', 'value'),
        State('url', 'search'),
        State('url', 'pathname'), #NEW
        State('empskill_remove', 'value')
    ]
)
def empskill_submitprocess(submitbtn, closebtn, 
                        empdropdown, skilldropdown, leveldropdown,
                        search, pathname, empskill_remove):

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
    if eventid == 'empskill_submitbtn' and submitbtn:
        # OPEN MODAL
        openmodal = True

        inputs = [
            empdropdown,
            skilldropdown,
            leveldropdown
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
                if pathname == '/employees/employeeprofile/skillrecord':
                    # REF OKAY BUTTON TO EMPPROF
                    okay_href = f'/employees/employeeprofile?mode=edit&id={returnid}'
                # ELIF ORIGIN PAGE IS SKILLPROF
                elif pathname == '/skills/skillprofile/skillrecord':
                    # REF OKAY BUTTON TO SKILLPROF
                    okay_href = f'/skills/skillprofile?mode=edit&id={returnid}'

                # SAVE TO DB
                sqlcode = """
                INSERT INTO employee_skill(EMP_ID,SK_ID,SK_L)
                VALUES(%s, %s, %s)
                """
                values = [empdropdown, skilldropdown, leveldropdown]
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Employee's skill recorded!"
            # ELIF MODE IS EDIT
            elif mode == 'edit':
                empskill_id = parse_qs(parsed.query)['id'][0]

                # UPDATE DB QUERY
                sqlcode = """
                UPDATE public.employee_skill
                SET
                emp_id = %s,
                sk_id = %s,
                sk_l = %s,
                employee_skill_delete_ind = %s
                WHERE concat(public.employee_skill.emp_id,public.employee_skill.sk_id) = %s
                """
                to_delete = bool(empskill_remove) #checking asn_remove value (either true or false)
                values = [empdropdown, skilldropdown, leveldropdown, to_delete, f'{empskill_id}']
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "Employee's skill record updated!"

                # QUERY EMPID AND JOBID FROM ASNID
                sql_returnid = """
                SELECT emp_id, sk_id
                FROM public.employee_skill
                WHERE concat(public.employee_skill.emp_id,public.employee_skill.sk_id) = %s
                """
                values_returnid = [f'{empskill_id}']
                cols_returnid = ['emp_id', 'sk_id']
                returnidvalue = db.querydatafromdatabase(sql_returnid, values_returnid, cols_returnid)
                emp_id = int(returnidvalue['emp_id'][0])
                sk_id = int(returnidvalue['sk_id'][0])

                # IF ORIGIN PAGE IS EMPPROF
                if pathname == '/employees/employeeprofile/skillrecord':
                    # REF OKAY BUTTON TO EMPPROF
                    okay_href = f'/employees/employeeprofile?mode=edit&id={emp_id}'
                # ELIF ORIGIN PAGE IS SKILLPROF
                elif pathname == '/skills/skillprofile/skillrecord':
                    # REF OKAY BUTTON TO SKILLPROF
                    okay_href = f'/skills/skillprofile?mode=edit&id={sk_id}'

            else:
                raise PreventUpdate #can be a custom url error message
            
    # IF CLOSE BUTTON WAS CLICKED
    elif eventid == 'empskill_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]
