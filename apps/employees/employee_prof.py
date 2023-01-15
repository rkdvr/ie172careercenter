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
from apps.employees import add_empjob, add_emptraining, add_empskill

layout = html.Div(
    [
        # for testing
        # html.Div(
        #     [
        #         html.P('text', id='output'),
        #         html.Br()
        #     ]
        # ),
        html.Div( # This div shall contain all dcc.Store objects
            [
                dcc.Store(id='empprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Employee Profile"),
        html.Hr(),        
        #PERSONAL INFORMATION---------------------------------------------------------------
        #First Name
        dbc.Row(
            [
                dbc.Label("First Name", width=2),
                dbc.Col(
                    dbc.Input(id="emp_firstname", placeholder="Enter first name", type="text"),
                    width=4,
                )
            ],
            className="mb-3",
        ),
        #Last Name
        dbc.Row(
            [
                dbc.Label("Last Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="emp_lastname", placeholder="Enter last name"
                    ),
                    width=4,
                ),
            ],
            className="mb-3",
        ),
        #SSS Number
        dbc.Row(
            [
                dbc.Label("SSS Number", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="emp_sssNum", placeholder="Enter SSS Number"
                    ),
                    width=4,
                ),
            ],
            className="mb-3",
        ),
        #Address
        dbc.Row(
            [
                dbc.Label("Address", width=2),
                dbc.Col(
                    dbc.Textarea(
                        id="emp_add", placeholder="Enter complete address", 
                    ),
                    width=4
                )
            ],
            className="mb-3",
        ),
        #Department
        dbc.Row(
            [
                dbc.Label("Department", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="emp_dept", placeholder="Enter department"
                    ),
                    width=4,
                ),
            ],
            className="mb-3",
        ),
        html.Br(),
        html.Br(),

        # HIDDEN ELEMENTS---------------------------------------------------------------------------------
        html.Div(
            [
                #JOB HISTORY-----------------------------------------------------------------------
                html.Div(
                    [
                        html.H4('Job History'),
                        html.Div(
                            "This will contain the table for job history.",
                            id='emp_jobhistory'
                        ),
                        html.Br(),
                        html.Div(
                            [
                                dbc.Button("Add Job Record", id="add_emp_job", n_clicks=0, color= 'secondary'),
                            ]
                        ), 
                        html.Br(),
                    ],
                    id='emp_jobhistory_div'
                ),
                        
                #TRAINING HISTORY-----------------------------------------------------------------------
                html.Div(
                    [
                        html.H3('Training History'),
                        dbc.Row(
                            "Insert table of training history here.",
                            id='emp_traininghistory'
                        ),
                        html.Br(),
                        html.Div(
                            [
                                dbc.Button("Add Training Record", id="add_emp_training", n_clicks=0, color= 'secondary'),
                            ]
                        ), 
                        html.Br(),
                    ],
                    id='emp_traininghistory_div'
                ),
                
                #SKILL RECORD---------------------------------------------------------------------------
                html.Div(
                    [
                        html.H3('Skills'),
                        dbc.Row(
                            "Insert table of skills here.",
                            id='emp_skillrecord'
                        ),
                        html.Br(),
                        html.Div(
                            [
                                dbc.Button("Add Skill Record", id="add_emp_skill", n_clicks=0, color= 'secondary'),
                            ]
                        ),
                        html.Br(),
                    ],
                    id='emp_skillrecord_div'
                ),

                #DELETE------------------------------------------------------------------------------------
                html.Div(
                    [
                        dbc.Row(           
                            [
                                dbc.Label("Remove Employee?", width=2, style={'color': 'red'}),
                                dbc.Col(
                                    dbc.Checklist(
                                        id='emp_removerecord',
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
                    id='emp_removerecord_div',
                ),
            ],
            id='emp_editelements_div'
        ),

        #SUBMIT------------------------------------------------------------------------------------------
        dbc.Button("Submit", color= 'warning', id='empprof_submitbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody('temp message', id='empprof_feedbackmsg'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="empprof_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                    )
                ),
            ],
            id="empprof_modal",
            is_open=False,
        )
    ]
)

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("empprof_modal", "is_open"),
        Output("empprof_feedbackmsg", "children"),
        Output("empprof_closebtn", "href")
    ],
    [
        Input("empprof_submitbtn", "n_clicks"),
        Input("empprof_closebtn", "n_clicks"),
    ],
    [
        State('emp_firstname', 'value'),
        State('emp_lastname', 'value'),
        State('emp_sssNum', 'value'),
        State('emp_add', 'value'),
        State('emp_dept', 'value'),
        State('url', 'search'),
        State('emp_removerecord', 'value'),
    ]
)
def empprof_submitprocess(submitbtn, closebtn,
                        empfirst, emplast, empsss, empaddress, empdept,
                        search, empremove): 

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
    if eventid == 'empprof_submitbtn' and submitbtn:
        
        # OPEN MODAL
        openmodal = True

        inputs = [
            empfirst, 
            emplast,
            empsss,
            empaddress,
            empdept
        ] 

        # IF INVALID INPUTS,
        if not all(inputs):
            # GIVE ERROR PROMPT
            feedbackmsg = "Please provide all inputs correctly."
        elif len(empaddress) > 256:
            # GIVE ERROR PROMPT
            feedbackmsg = "Address is too long"

        # ELIF VALID INPUTS
        else:
            # REF OKAY BUTTON TO EMP HOME
            okay_href = '/employees'

            parsed = urlparse(search)
            mode = parse_qs(parsed.query)['mode'][0]

            # IF MODE IS ADD
            if mode == 'add':
                # SAVE TO DB
                sqlcode = """
                INSERT INTO employees (EMP_FN,EMP_LN,EMP_SSS,EMP_ADR,DEPT)
                VALUES (%s, %s, %s, %s, %s)
                """
                values = [empfirst, emplast, empsss, empaddress, empdept]
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Employee Added!"

            # ELIF MODE IS EDIT
            elif mode == 'edit':
                emp_id = parse_qs(parsed.query)['id'][0]

                # UPDATE DB
                sqlcode = """
                UPDATE employees
                SET
                emp_fn = %s,
                emp_ln = %s,
                emp_sss = %s,
                emp_adr = %s,
                dept = %s,
                employee_delete_ind = %s
                WHERE emp_id = %s
                """
                to_delete = bool(empremove) #checking empremove value (either true or false)
                values = [empfirst, emplast, empsss, empaddress, empdept, to_delete, emp_id]
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "User has been updated!"
            else:
                raise PreventUpdate #can be a custom url error message
    # ELIF CLOSE BUTTON WAS CLICKED,
    elif eventid == 'empprof_closebtn' and closebtn:
        # CLOSE MODAL
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]

# LOAD ELEMENTS UPON PAGE LOAD--------------------------------------------------------------------------------
@app.callback(
    [
        Output('empprof_toload', 'data'),
        Output('emp_editelements_div', 'style'),
        Output("add_emp_job", "href"),
        Output("add_emp_training", "href"),
        Output("add_emp_skill", "href"),
        Output('emp_jobhistory', 'children'),
        Output('emp_traininghistory', 'children'),
        Output('emp_skillrecord', 'children')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search') 
    ]
)
def triggereditmode(pathname, search):
    # UPON PAGE LOAD, IF PATHNAME IS EMPLOYEE PROFILE
        # DETERMINE IF MODE IS EDIT OR ADD
        # UPDATE STYLE OF EDIT ELEMENTS
        # ADD REFERENCE TO FORMS TO ADD TO JUNCTION TABLES
        
    if pathname == '/employees/employeeprofile':
       
        # are we on add or edit mode?
        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None
        # if to_load = 0, then not to_load -> not 0 -> not False -> True

        #EMPTY VALUES IF ADD MODE
        empjob_href = ""
        emptraining_href = ""
        empskill_href = ""
        assignment_table = "" 
        emptr_table = ""
        empskills_table = ""

        # VALUES IF EDIT MODE
        if to_load:
            parsed = urlparse(search)
            emp_id = parse_qs(parsed.query)['id'][0]
            # ADD REFERENCE TO FORMS TO ADD TO JUNCTION TABLES
            empjob_href = f"/employees/employeeprofile/assignmentprofile?mode=add&id={emp_id}"
            emptraining_href = f"/employees/employeeprofile/participantprofile?mode=add&id={emp_id}"
            empskill_href = f"/employees/employeeprofile/skillrecord?mode=add&id={emp_id}"

            # LOAD ASSIGNMENT CHILDREN--------------------------------------------------------
            sql_assignment = """
            SELECT job_n, asn_sd, asn_ed, asn_id
                FROM employees
                INNER JOIN assignments on assignments.emp_id = employees.emp_id
                INNER JOIN jobs on jobs.job_id = assignments.job_id
            WHERE assignment_delete_ind = False 
				AND job_delete_ind = False
                AND employees.emp_id = %s
            """
            values_assignment = [emp_id]
            colnames_assignment = ['Job Name', 'Start Date', 'End Date', 'ID']
            assignmentdf = db.querydatafromdatabase(sql_assignment, values_assignment, colnames_assignment)

            if assignmentdf.shape[0]:
                # ADD A BUTTON PER ROW THAT CAN EDIT ITS CONTENTS
                buttons =[]
                for asn_id in assignmentdf['ID']:
                    buttons += [
                        dbc.Button(
                            '⚙️ Edit or Remove', 
                            href=f"/employees/employeeprofile/assignmentprofile?mode=edit&id={asn_id}",
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
            
            # LOAD EMP-TRAINING CHILDREN----------------------------------------------------------------------------
            sql_emptr = """
            SELECT tr_n, tr_s, tr_ed, employee_training.employee_training_delete_ind, concat(employee_training.emp_id, employee_training.tr_id)
                FROM employees
                INNER JOIN employee_training on employee_training.emp_id = employees.emp_id
                INNER JOIN trainings on employee_training.tr_id = trainings.tr_id
            WHERE employees.emp_id = %s 
                and employee_training.employee_training_delete_ind = False
                and employees.employee_delete_ind = False
                and trainings.training_delete_ind = False
            """
            values_emptr = [emp_id]
            colnames_emptr = ['Training Name', 'Start Date', 'End Date', 'DELETED','ID']
            emp_trainings_df = db.querydatafromdatabase(sql_emptr, values_emptr, colnames_emptr)

            if emp_trainings_df.shape[0]:
                # ADD A BUTTON PER ROW THAT CAN EDIT ITS CONTENTS
                
                buttons =[]
                for emptr_id in emp_trainings_df['ID']:
                    buttons += [
                        dbc.Button(
                            '⚙️ Edit or Remove', 
                            href=f"/employees/employeeprofile/participantprofile?mode=edit&id={emptr_id}",
                            size='sm',
                            color='dark'
                        )
                    ]
                
                # ADD NEW COLUMNS
                # emp_trainings_df['Status'] = deleted
                emp_trainings_df['Action'] = buttons 
                emp_trainings_df.drop('DELETED', axis=1, inplace=True)
                emp_trainings_df.drop('ID', axis=1, inplace=True)

                # LOAD TABLES
                emptr_table = html.Div(
                    dbc.Table.from_dataframe(
                        emp_trainings_df, 
                        striped=True, 
                        bordered=True, 
                        hover=True, 
                        size='sm',
                        style={'text-align': 'center'}
                    )
                )
            else:
                # RAISE NULL PROMPT
                emptr_table = "No records to display"

            # LOAD EMP-SKILL CHILDREN------------------------------------------------------------------
            sql_empsk = """
            SELECT sk_n, sk_c, sk_l, concat(employee_skill.emp_id,employee_skill.sk_id)
            FROM employees
                INNER JOIN employee_skill on employee_skill.emp_id = employees.emp_id
                INNER JOIN skills on employee_skill.sk_id = skills.sk_id
            WHERE employees.emp_id = %s
                AND employee_skill.employee_skill_delete_ind = False
				AND skills.skill_delete_ind = False
            """
            values_empsk = [emp_id]
            colnames_empsk = ['Skill', 'Category', 'Level', 'ID']
            emp_skills_df = db.querydatafromdatabase(sql_empsk, values_empsk, colnames_empsk)

            if emp_skills_df.shape[0]:
                # ADD A BUTTON PER ROW THAT CAN EDIT ITS CONTENTS
                buttons =[]
                for empsk_id in emp_skills_df['ID']:
                    buttons += [
                        dbc.Button(
                            '⚙️ Edit or Remove', 
                            href=f"/employees/employeeprofile/skillrecord?mode=edit&id={empsk_id}",
                            size='sm',
                            color='dark'
                        )
                    ]
                
                # ADD COLUMN FOR EDIT BUTTONS
                emp_skills_df['Action'] = buttons #add column named action containing the buttons
                emp_skills_df.drop('ID', axis=1, inplace=True) #remove id col -> axis: 1 - column, 0 - row

                # LOAD TABLES
                empskills_table = html.Div(
                    dbc.Table.from_dataframe(
                        emp_skills_df, 
                        striped=True, 
                        bordered=True, 
                        hover=True, 
                        size='sm',
                        style={'text-align': 'center'}
                    )
                )
            else:
                # RAISE NULL PROMPT
                empskills_table = "No records to display"

    else:
        raise PreventUpdate

    return [to_load, removediv_style, empjob_href, emptraining_href, empskill_href, assignment_table, emptr_table, empskills_table]

#LOAD INFORMATION TO INTERFACE BASED ON MODE--------------------------------------------------------------------------------
@app.callback(
    [
        Output('emp_firstname', 'value'),
        Output('emp_lastname', 'value'),
        Output('emp_sssNum', 'value'),
        Output('emp_add', 'value'),
        Output('emp_dept', 'value')
    ],
    [
        Input('empprof_toload', 'modified_timestamp'),
    ],
    [
        State('empprof_toload', 'data'),
        State('url', 'search')
    ]
)
def loademployeeinfo(timestamp, to_load, search):

    #IF TO_LOAD IS 1 (MODE IS EDIT)
    if to_load == 1:
        parsed = urlparse(search)
        emp_id = parse_qs(parsed.query)['id'][0]
  
        #lOAD BASIC INFO----------------------------------------------------------------
        #1 query details from database
        sql = """
        SELECT EMP_FN,EMP_LN,EMP_SSS,EMP_ADR,DEPT
        FROM employees
        WHERE emp_id = %s
        """
        values =[emp_id]
        colnames =['firstname', 'lastname', 'sssnumber', 'address', 'department']
        df = db.querydatafromdatabase(sql, values, colnames) #df = dataframe

        #2 load values to the interface
        emp_first = df['firstname'][0]
        emp_last = df['lastname'][0]
        emp_sss = df['sssnumber'][0]
        emp_address = df['address'][0]
        emp_dept = df['department'][0]
        
        return [emp_first, emp_last, emp_sss, emp_address, emp_dept]

    # ELSE, PREVENT UDPATE
    else:
        raise PreventUpdate