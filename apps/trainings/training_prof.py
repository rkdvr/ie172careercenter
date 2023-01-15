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
                dcc.Store(id='trainingprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2('Training Profile'),
        html.Hr(),
        #Training Name--------------------------------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Training Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="trainingprof_name", placeholder="Enter first name"
                    ),
                        width=4,
                ),
            ],
            className="mb-3",
        ),
        #Training Description----------------------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Description", width=2),
                dbc.Col(
                    dbc.Textarea(className="mb-3", placeholder="Enter description here", id="trainingprof_desc"),
                    width=4
                )
            ],
            className="mb-3",
        ),
        #Training Start and End Dates-----------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Start Date", width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id='trainingprof_start',
                    ),
                    width=2,
                ),
                dbc.Label("End Date", width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id='trainingprof_end',
                    ),
                    width=2,
                )  
            ],
            className="mb-3",
        ),
        html.Br(),
        #HIDDEN------------------------------------------------------------------------------------
        html.Div(
            [
                #Skills
                html.Div(
                    [
                        html.H3('Skills Acquired'),
                        dbc.Row(
                            "Insert table of skills here.",
                            id='training_skillslist'
                        ),
                        html.Br(),
                        html.Div(
                            [
                                dbc.Button("Add Skill Acquired", id="add_tr_skill", n_clicks=0, color= 'secondary'),
                            ]
                        ),
                        html.Br(),
                    ],
                    id='tr_skillrecord_div'
                ),
                #Employees
                html.Div(
                    [
                        html.H3('Employee Participants'),
                        dbc.Row(
                            "Insert table of training history here.",
                            id='tr_participants'
                        ),
                        html.Br(),
                        html.Div(
                            [
                                dbc.Button("Add Participants", id="add_tr_participant", n_clicks=0, color= 'secondary'),
                            ]
                        ), 
                        html.Br(),
                    ],
                    id='tr_participants'
                ),
                #Delete
                dbc.Row(           
                    [
                        dbc.Label("Delete Training?", width=2, style={'color': 'red'}),
                        dbc.Col(
                            dbc.Checklist(
                                id='training_removerecord',
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
            id='training_editmode_div'
        ),

        #SUBMIT------------------------------------------------------------------------------------------
        dbc.Button("Submit", color= 'warning', id='trainingprof_submitbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody('temp message', id='trainingprof_feedbackmsg'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="trainingprof_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                    )
                ),
            ],
            id="trainingprof_modal",
            is_open=False,
        )  
    ]
)

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("trainingprof_modal", "is_open"),
        Output("trainingprof_feedbackmsg", "children"),
        Output("trainingprof_closebtn", "href")
    ],
    [
        Input("trainingprof_submitbtn", "n_clicks"),
        Input("trainingprof_closebtn", "n_clicks"),
    ],
    [
        State('trainingprof_name', 'value'),
        State('trainingprof_desc', 'value'),
        State('trainingprof_start', 'date'),
        State('trainingprof_end', 'date'),
        State('url', 'search'),
        State('training_removerecord', 'value'),
    ]
)
def trainingprof_submitprocess(submitbtn, closebtn,
                        trainingname, trainingdesc, trainingstart, trainingend,
                        search, trainingremove): 

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
    if eventid == 'trainingprof_submitbtn' and submitbtn:
        # OPEN MODAL
        openmodal = True

        inputs = [
            trainingname, 
            trainingdesc,
            trainingstart,
            trainingend
        ] 

        # IF INVALID INPUTS,
        if not all(inputs):
            # GIVE ERROR PROMPTS
            feedbackmsg = "Please provide all inputs correctly."
        elif len(trainingname) > 100:
            # GIVE ERROR PROMPTS
            feedbackmsg = "Training name is too long. (>100)"

        # ELIF VALID INPUTS
        else:
            # REF OKAY BUTTON TO TRAINING HOME
            okay_href = '/trainings'

            parsed = urlparse(search)
            mode = parse_qs(parsed.query)['mode'][0]      

            # IF MODE IS ADD
            if mode == 'add':
                # SAVE TO DB
                sqlcode = """
                INSERT INTO trainings(tr_n, tr_ds, tr_s, tr_ed)
                VALUES(%s, %s, %s, %s)
                """
                values = [trainingname, trainingdesc, trainingstart, trainingend]
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Training Added!"

            # ELIF MODE IS EDIT
            elif mode == 'edit':
                tr_id = parse_qs(parsed.query)['id'][0]              
                
                # UPDATE DB QUERY
                sqlcode = """
                UPDATE trainings
                SET
                tr_n = %s,
                tr_ds = %s,
                tr_s = %s,
                tr_ed = %s,
                training_delete_ind = %s
                WHERE tr_id = %s
                """

                to_delete = bool(trainingremove)
                
                values = [trainingname, trainingdesc, trainingstart, trainingend, to_delete, tr_id]
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "Training has been updated!"
            else:
                raise PreventUpdate #can be a custom URL ERROR MESSAGE

    # ELIF CLOSE BUTTON WAS CLICKED,
    elif eventid == 'trainingprof_closebtn' and closebtn:
        # CLOSE MODAL
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]

# LOAD ELEMENTS UPON PAGE LOAD--------------------------------------------------------------------------------
@app.callback(
    [
        Output('trainingprof_toload', 'data'),
        Output('training_editmode_div', 'style'),
        Output('add_tr_skill', 'href'),
        Output('add_tr_participant', 'href'),
        Output('training_skillslist', 'children'),
        Output('tr_participants', 'children'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def triggereditmode (pathname, search):
    # UPON PAGE LOAD, IF PATHNAME IS EMPLOYEE PROFILE
        # DETERMINE IF MODE IS EDIT OR ADD
        # UPDATE STYLE OF EDIT ELEMENTS
        # ADD REFERENCE TO FORMS TO ADD TO JUNCTION TABLES

    if pathname == '/trainings/trainingprofile':

        parsed = urlparse(search)
        mode = parse_qs(parsed.query)['mode'][0]        
        to_load = 1 if mode == 'edit' else 0
        editelementsdiv = None if to_load else {'display': 'none'}

        #EMPTY VALUES IF ADD MODE
        trskill_href = ""
        trparticipant_href = ""
        skill_table = ""
        participantlist = ""
        
        # VALUES IF EDIT MODE
        if to_load:
            parsed = urlparse(search)
            tr_id = parse_qs(parsed.query)['id'][0]
            # ADD REFERENCE TO FORMS TO ADD TO JUNCTION TABLES
            trskill_href = f"/trainings/trainingprofile/trainingskillprofile?mode=add&id={tr_id}"
            trparticipant_href = f"/trainings/trainingprofile/participantprofile?mode=add&id={tr_id}"

            # LOAD TR-SKILL CHILDREN--------------------------------------------------------
            sql_trskill = """
            SELECT sk_n, sk_ds, sk_c, concat(skill_training.sk_id, skill_training.tr_id)
                FROM trainings
                INNER JOIN skill_training on skill_training.tr_id = trainings.tr_id
                INNER JOIN skills on skills.sk_id = skill_training.sk_id
            WHERE trainings.tr_id = %s 
                AND training_delete_ind = false
                AND skill_delete_ind = False
                AND skill_training_delete_ind = False
            """
            values_trskill = [tr_id]
            colnames_trskill = ['Skill', 'Description', 'Category', 'ID']
            trainingskilldf = db.querydatafromdatabase(sql_trskill, values_trskill, colnames_trskill)

            if trainingskilldf.shape[0]:
                # ADD A BUTTON PER ROW THAT CAN EDIT ITS CONTENTS
                buttons =[]
                for trskill_id in trainingskilldf['ID']:
                    buttons += [
                        dbc.Button(
                            '⚙️ Edit or Remove', 
                            href=f"/trainings/trainingprofile/trainingskillprofile?mode=edit&id={trskill_id}",
                            size='sm',
                            color='dark'
                        )
                    ]
                
                # ADD COLUMN FOR EDIT BUTTONS
                trainingskilldf['Action'] = buttons #add column named action containing the buttons
                trainingskilldf.drop('ID', axis=1, inplace=True) #remove id col -> axis: 1 - column, 0 - row

                # LOAD TABLES
                skill_table = html.Div(
                    dbc.Table.from_dataframe(
                        trainingskilldf, 
                        striped=True, 
                        bordered=True, 
                        hover=True, 
                        size='sm',
                        style={'text-align': 'center'}
                    )
                )
            else:
                # RAISE NULL PROMPT
                skill_table = "No records to display"

            # LOAD PARTICIPANT CHILDREN--------------------------------------------------------
            sql_tremp = """
            SELECT concat(emp_fn, ' ', emp_ln), dept, concat(employee_training.emp_id, employee_training.tr_id)
                FROM employees
                INNER JOIN employee_training on employee_training.emp_id = employees.emp_id
                INNER JOIN trainings on employee_training.tr_id = trainings.tr_id
            WHERE trainings.tr_id = %s 
                and employee_training.employee_training_delete_ind = False
                and employees.employee_delete_ind = False
                and trainings.training_delete_ind = False
            """
            values_tremp = [tr_id]
            colnames_tremp = ['Participant Name', 'Dept', 'ID']
            emp_trainings_df = db.querydatafromdatabase(sql_tremp, values_tremp, colnames_tremp)

            if emp_trainings_df.shape[0]:
                # ADD A BUTTON PER ROW THAT CAN EDIT ITS CONTENTS
                buttons =[]
                for tremp_id in emp_trainings_df['ID']:
                    buttons += [
                        dbc.Button(
                            '⚙️ Edit or Remove', 
                            href=f"/trainings/trainingprofile/participantprofile?mode=edit&id={tremp_id}",
                            size='sm',
                            color='dark'
                        )
                    ]
                
                # ADD COLUMN FOR EDIT BUTTONS
                emp_trainings_df['Action'] = buttons #add column named action containing the buttons
                emp_trainings_df.drop('ID', axis=1, inplace=True) #remove id col -> axis: 1 - column, 0 - row

                # LOAD TABLES
                participantlist = html.Div(
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
                participantlist = "No records to display"

    else:
        raise PreventUpdate

    return [to_load, editelementsdiv, trskill_href, trparticipant_href, skill_table, participantlist]

#LOAD INFORMATION TO INTERFACE
@app.callback(
    [
        Output('trainingprof_name', 'value'),
        Output('trainingprof_desc', 'value'),
        Output('trainingprof_start', 'date'),
        Output('trainingprof_end', 'date')
    ],
    [
        Input('trainingprof_toload', 'modified_timestamp')
    ],
    [
        State('trainingprof_toload', 'data'),
        State('url', 'search')
    ]
)
def loadtraininginfo(timestamp, to_load, search):
    if to_load == 1:
        parsed = urlparse(search)
        tr_id = parse_qs(parsed.query)['id'][0] #the key is 'id' in URL
        
        #LOAD TRAINING INFO------------------------------------------------------------
        #1 QUERY DETAILS FROM DATABASE
        sql = """
        SELECT tr_n, tr_ds, tr_s, tr_ed
        FROM trainings
        WHERE tr_id = %s
        """
        values =[tr_id]
        colnames =['trainingname', 'trainingdesc', 'trainingstart', 'trainingend']
        df = db.querydatafromdatabase(sql, values, colnames) #df = dataframe

        #2 LOAD VALUES ON INTERFACE
        trainingname = df['trainingname'][0]
        trainingdesc = df['trainingdesc'][0]
        trainingstart = df['trainingstart'][0]
        trainingend = df['trainingend'][0]

        return [trainingname, trainingdesc, trainingstart, trainingend]

    else:
        raise PreventUpdate