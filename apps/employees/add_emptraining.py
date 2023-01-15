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
                dcc.Store(id='emptraining_toload', storage_type='memory', data=0),
            ],
        ),
        html.H2("Employee Training Records"),
        html.Hr(),
        #EMPLOYEE DROPDOWN
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Employee Name", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='emp_trdropdown',
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
            id='emp_trdropdown_div'
        ),
        #TRAINING DROPDOWN
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Training Name", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='training_dropdown',
                                placeholder = 'Select Training',
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
            id='emptraining_trinput'
        ),
        html.Br(),
        #DELETE
        html.Div(
            [
                dbc.Row(           
                    [
                        dbc.Label("Remove Employee Training Record?", width=2, style={'color': 'red'}),
                        dbc.Col(
                            dbc.Checklist(
                                id='emptraining_remove',
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
            id='emptraining_remove_div',
        ),
        #SUBMIT
        dbc.Button("Submit", color= 'warning', id='emptraining_submitbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody('temp message', id='emptraining_feedbackmsg'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="emptraining_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                    )
                ),
            ],
            id="emptraining_modal",
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
            id='emptraining_disclaimer'
        )
    ]
)

#lOAD ELEMENTS UPON PAGE LOAD-------------------------------------------------------------------------------
@app.callback(
    [
        Output('emptraining_toload', 'data'),
        Output('emptraining_remove_div', 'style')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def loadparticipantprofile(pathname, search):

    if pathname == '/employees/employeeprofile/participantprofile' or pathname == '/trainings/trainingprofile/participantprofile':

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
        Output('emp_trdropdown', 'value'),
        Output('training_dropdown', 'value'),
        Output('emp_trdropdown', 'options'),
        Output('training_dropdown', 'options'),
        Output('emp_trdropdown', 'disabled'),
        Output('training_dropdown', 'disabled'),
    ],
    [
        Input('emptraining_toload', 'modified_timestamp'),
    ],
    [
        State('emptraining_toload', 'data'),
        State('url', 'search'),
        State('url', 'pathname')
    ]
)
def loadparticipationinfo (timestamp, to_load, search, pathname):
    
    #LOADING VALUES AND OPTIONS---------------
    parsed = urlparse(search)
    
    # INITIALIZE SQL QUERIES
    sql_restrictemp = ""
    values_restrictemp = []
    cols_restrictemp = ['label', 'value']
    
    sql_restricttraining = ""
    values_restricttraining = []
    cols_restricttraining = ['label', 'value']

    #GETTING NECESSARY IDS
    #IF PAGE IS IN EDIT MODE,
    if to_load:
        participant_id = parse_qs(parsed.query)['id'][0]

        employee_disabled = True
        training_disabled = True

        #GET IDS FROM JUNCTION ID
        sql_emptraininginfo = """
        SELECT public.employee_training.emp_id, public.employee_training.tr_id
            FROM public.employee_training
            INNER JOIN trainings on public.employee_training.tr_id = trainings.tr_id
            INNER JOIN employees on public.employee_training.emp_id = employees.emp_id
        WHERE concat(public.employee_training.emp_id,public.employee_training.tr_id) = %s
        """
        values_emptraininginfo = [f'{participant_id}']
        col_emptraininginfo = ['emp_id','tr_id']
        emptraininginfo_table = db.querydatafromdatabase(sql_emptraininginfo, values_emptraininginfo, col_emptraininginfo)
        employee_id = int(emptraininginfo_table['emp_id'][0])
        training_id = int(emptraininginfo_table['tr_id'][0])

        # LOAD VALUE OF CURRENT ENTRY
        sql_restrictemp += """
        (SELECT CONCAT(emp_fn,' ',emp_ln) as label, emp_id as value
            FROM employees
            WHERE emp_id = %s)
        UNION
        """
        values_restrictemp += [employee_id]

        sql_restricttraining += """
        (SELECT tr_n as label, tr_id as value
            FROM trainings
            WHERE tr_id = %s)
        UNION
        """
        values_restricttraining += [training_id]

    #ELIF PAGE IS IN ADD MODE,
    elif not to_load:
        loadedID = parse_qs(parsed.query)['id'][0]

        #IF ORIGIN PAGE IS EMPLOYEE PROFILE
        if pathname == '/employees/employeeprofile/participantprofile':
            #lOAD EMP ID
            employee_id = loadedID
            training_id = None
            employee_disabled = True
            training_disabled = False
        #ELIF ORIGIN PAGE IS TRAINING PROFILE
        elif pathname == '/trainings/trainingprofile/participantprofile':           
            #EMPTY EMPLOYEE
            employee_id = None
            training_id = loadedID
            employee_disabled = False
            training_disabled = True
    
    else:
        raise PreventUpdate
    
    # AFTER RETRIEVING THE NECESSARY IDS, LOAD RESTRICTED DROPDOWN VALUES
    #Restrict values of employee dropdown
    sql_restrictemp += """
    (SELECT CONCAT(emp_fn,' ',emp_ln) as label, emp_id as value
        FROM employees
        WHERE employees.employee_delete_ind = FALSE
    EXCEPT SELECT CONCAT(emp_fn,' ',emp_ln), employee_training.emp_id
        FROM employee_training
        INNER JOIN employees ON employees.emp_id = employee_training.emp_id
        WHERE employee_training.tr_id = %s)
    """
    values_restrictemp += [training_id]
    employeerestricted = db.querydatafromdatabase(sql_restrictemp, values_restrictemp, cols_restrictemp)
    employee_options = employeerestricted.to_dict('records')

    #Restrict values of training dropdown
    sql_restricttraining += """
    (SELECT tr_n as label, tr_id as value
        FROM trainings
        WHERE trainings.training_delete_ind = FALSE
    EXCEPT SELECT tr_n, employee_training.tr_id
        FROM employee_training
        INNER JOIN trainings ON trainings.tr_id = employee_training.tr_id
        WHERE employee_training.emp_id = %s)
    """
    values_restricttraining += [employee_id]
    trainingrestricted = db.querydatafromdatabase(sql_restricttraining, values_restricttraining, cols_restricttraining)
    training_options = trainingrestricted.to_dict('records')

    return [employee_id, training_id, employee_options, training_options, employee_disabled, training_disabled]

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("emptraining_modal", "is_open"),
        Output("emptraining_feedbackmsg", "children"),
        Output("emptraining_closebtn", "href")
    ],
    [
        Input("emptraining_submitbtn", "n_clicks"),
        Input("emptraining_closebtn", "n_clicks"),
    ],
    [
        State('emp_trdropdown', 'value'),
        State('training_dropdown', 'value'),
        State('url', 'search'),
        State('url', 'pathname'), #NEW
        State('emptraining_remove', 'value')
    ]
)
def emptraining_submitprocess(submitbtn, closebtn, 
                        empdropdown, trainingdropdown,
                        search, pathname, emptraining_remove):

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
    if eventid == 'emptraining_submitbtn' and submitbtn:
        # OPEN MODAL
        openmodal = True

        inputs = [
            empdropdown,
            trainingdropdown
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
                if pathname == '/employees/employeeprofile/participantprofile':
                    # REF OKAY BUTTON TO EMPPROF
                    okay_href = f'/employees/employeeprofile?mode=edit&id={returnid}'
                # ELIF ORIGIN PAGE IS TRAININGPROF
                elif pathname == '/trainings/trainingprofile/participantprofile':
                    # REF OKAY BUTTON TO TRAININGPROF
                    okay_href = f'/trainings/trainingprofile?mode=edit&id={returnid}'

                # SAVE TO DB
                sqlcode = """
                INSERT INTO employee_training(EMP_ID,TR_ID)
                VALUES(%s, %s)
                """
                values = [empdropdown, trainingdropdown]
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Training participation recorded!"
            # ELIF MODE IS EDIT
            elif mode == 'edit':
                emptraining_id = parse_qs(parsed.query)['id'][0]

                # UPDATE DB QUERY
                sqlcode = """
                UPDATE public.employee_training
                SET
                emp_id = %s,
                tr_id = %s,
                employee_training_delete_ind = %s
                WHERE concat(public.employee_training.emp_id,public.employee_training.tr_id) = %s
                """
                to_delete = bool(emptraining_remove) #checking asn_remove value (either true or false)
                values = [empdropdown, trainingdropdown, to_delete, f'{emptraining_id}']
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "Training participation details updated!"

                # QUERY RETURN IDS
                sql_returnid = """
                SELECT emp_id, tr_id
                FROM public.employee_training
                WHERE concat(public.employee_training.emp_id,public.employee_training.tr_id) = %s
                """
                values_returnid = [f'{emptraining_id}']
                cols_returnid = ['emp_id', 'tr_id']
                returnidvalue = db.querydatafromdatabase(sql_returnid, values_returnid, cols_returnid)
                emp_id = int(returnidvalue['emp_id'][0])
                tr_id = int(returnidvalue['tr_id'][0])

                # IF ORIGIN PAGE IS EMPPROF
                if pathname == '/employees/employeeprofile/participantprofile':
                    # REF OKAY BUTTON TO EMPPROF
                    okay_href = f'/employees/employeeprofile?mode=edit&id={emp_id}'
                # ELIF ORIGIN PAGE IS TRAININGPROF
                elif pathname == '/trainings/trainingprofile/participantprofile':
                    # REF OKAY BUTTON TO TRAININGPROF
                    okay_href = f'/trainings/trainingprofile?mode=edit&id={tr_id}'

            else:
                raise PreventUpdate #can be a custom url error message
            
    # IF CLOSE BUTTON WAS CLICKED
    elif eventid == 'emptraining_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]
