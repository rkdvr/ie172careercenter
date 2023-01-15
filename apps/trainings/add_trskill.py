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
                dcc.Store(id='skilltraining_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Skill Training Programs"),
        html.Hr(),
        #SKILL NAME
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Skill Name", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='skill_trdropdown',
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
        #TRAINING NAME
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Training Name", width=2),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='training_skdropdown',
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
            id='sktraining_input'
        ),
        html.Br(),
        #DELETE
        html.Div(
            [
                dbc.Row(           
                    [
                        dbc.Label("Remove Skill Training Program?", width=2, style={'color': 'red'}),
                        dbc.Col(
                            dbc.Checklist(
                                id='skilltraining_remove',
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
            id='skilltraining_remove_div',
        ),
        #SUBMIT
        dbc.Button("Submit", color= 'warning', id='skilltraining_submitbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody('temp message', id='skilltraining_feedbackmsg'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="skilltraining_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                    )
                ),
            ],
            id="skilltraining_modal",
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
            id='trskill_disclaimer'
        )
    ]
)

#lOAD ELEMENTS UPON PAGE LOAD-------------------------------------------------------------------------------
@app.callback(
    [
        Output('skilltraining_toload', 'data'),
        Output('skilltraining_remove_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def loadskilltrainingelements(pathname, search):

    if pathname == '/trainings/trainingprofile/trainingskillprofile' or pathname == '/skills/skillprofile/trainingskillprofile':

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
        Output('skill_trdropdown', 'value'),
        Output('training_skdropdown', 'value'),
        Output('skill_trdropdown', 'options'),
        Output('training_skdropdown', 'options'),
        Output('skill_trdropdown', 'disabled'),
        Output('training_skdropdown', 'disabled'),
    ],
    [
        Input('skilltraining_toload', 'modified_timestamp'),
    ],
    [
        State('skilltraining_toload', 'data'),
        State('url', 'search'),
        State('url', 'pathname')
    ]
)
def loadparticipationinfo (timestamp, to_load, search, pathname):
    
    #LOADING VALUES AND OPTIONS---------------
    parsed = urlparse(search)
     
    # INITIALIZE SQL QUERIES
    sql_restrictskill = ""
    values_restrictskill = []
    cols_restrictskill = ['label', 'value']
    
    sql_restricttraining = ""
    values_restricttraining = []
    cols_restricttraining = ['label', 'value']

    #GETTING NECESSARY IDS
    #IF PAGE IS IN EDIT MODE,
    if to_load:
        sktraining_id = parse_qs(parsed.query)['id'][0]

        skill_disabled = True
        training_disabled = True

        #GET IDS FROM JUNCTION ID
        sql_sktraininginfo = """
        SELECT public.skill_training.sk_id, public.skill_training.tr_id
            FROM public.skill_training
            INNER JOIN trainings on public.skill_training.tr_id = trainings.tr_id
            INNER JOIN skills on public.skill_training.sk_id = skills.sk_id
        WHERE concat(public.skill_training.sk_id,public.skill_training.tr_id) = %s
        """
        values_sktraininginfo = [f'{sktraining_id}']
        col_sktraininginfo = ['sk_id','tr_id']
        sktraininginfo_table = db.querydatafromdatabase(sql_sktraininginfo, values_sktraininginfo, col_sktraininginfo)
        skill_id = int(sktraininginfo_table['sk_id'][0])
        training_id = int(sktraininginfo_table['tr_id'][0])

        # LOAD VALUE OF CURRENT ENTRY
        sql_restrictskill += """
        (SELECT sk_n as label, sk_id as value
            FROM skills
            WHERE sk_id = %s)
        UNION
        """
        values_restrictskill += [skill_id]

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

        #IF ORIGIN PAGE IS SKILL PROFILE
        if pathname == '/skills/skillprofile/trainingskillprofile':
            #lOAD SK ID
            skill_id = loadedID
            training_id = None
            skill_disabled = True
            training_disabled = False
        
        #ELIF ORIGIN PAGE IS TRAINING PROFILE
        elif pathname == '/trainings/trainingprofile/trainingskillprofile':
            #LOAD TRAINING ID
            skill_id = None
            training_id = loadedID
            skill_disabled = False
            training_disabled = True      
    
    else:
        raise PreventUpdate

    # AFTER RETRIEVING THE NECESSARY IDS, LOAD RESTRICTED DROPDOWN VALUES
    #Restrict values of skill dropdown
    sql_restrictskill += """
	(SELECT sk_n, sk_id
		FROM skills
        WHERE skills.skill_delete_ind = false
	EXCEPT SELECT sk_n, skill_training.sk_id
		FROM skill_training
		INNER JOIN skills ON skills.sk_id = skill_training.sk_id
		WHERE skill_training.tr_id = %s)
    """
    values_restrictskill += [training_id]
    skillrestricted = db.querydatafromdatabase(sql_restrictskill, values_restrictskill, cols_restrictskill)
    skill_options = skillrestricted.to_dict('records')

    #Restrict values of training dropdown
    sql_restricttraining += """
    (SELECT tr_n as label, tr_id as value
        FROM trainings
        WHERE trainings.training_delete_ind = FALSE
    EXCEPT SELECT tr_n, skill_training.tr_id
        FROM skill_training
        INNER JOIN trainings ON trainings.tr_id = skill_training.tr_id
        WHERE skill_training.sk_id = %s)
    """
    values_restricttraining += [skill_id]
    trainingrestricted = db.querydatafromdatabase(sql_restricttraining, values_restricttraining, cols_restricttraining)
    training_options = trainingrestricted.to_dict('records')
    
    return [skill_id, training_id, skill_options, training_options, skill_disabled, training_disabled]

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("skilltraining_modal", "is_open"),
        Output("skilltraining_feedbackmsg", "children"),
        Output("skilltraining_closebtn", "href")
    ],
    [
        Input("skilltraining_submitbtn", "n_clicks"),
        Input("skilltraining_closebtn", "n_clicks"),
    ],
    [
        State('skill_trdropdown', 'value'),
        State('training_skdropdown', 'value'),
        State('url', 'search'),
        State('url', 'pathname'), #NEW
        State('skilltraining_remove', 'value')
    ]
)
def skilltraining_submitprocess(submitbtn, closebtn, 
                        skilldropdown, trainingdropdown,
                        search, pathname, sktraining_remove):

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
    if eventid == 'skilltraining_submitbtn' and submitbtn:
        # OPEN MODAL
        openmodal = True

        inputs = [
            skilldropdown,
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
                # IF ORIGIN PAGE IS SKILLPROF
                if pathname == '/skills/skillprofile/trainingskillprofile':
                    # REF OKAY BUTTON TO SKILLPROF
                    okay_href = f'/skills/skillprofile?mode=edit&id={returnid}'
                # ELIF ORIGIN PAGE IS TRAININGPROF
                elif pathname == '/trainings/trainingprofile/trainingskillprofile':
                    # REF OKAY BUTTON TO TRAININGPROF
                    okay_href = f'/trainings/trainingprofile?mode=edit&id={returnid}'

                # SAVE TO DB
                sqlcode = """
                INSERT INTO skill_training(SK_ID,TR_ID)
                VALUES(%s, %s)
                """
                values = [skilldropdown, trainingdropdown]
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Training program for skill recorded!"

            # ELIF MODE IS EDIT
            elif mode == 'edit':
                # UPDATE DB QUERY
                sktraining_id = parse_qs(parsed.query)['id'][0]

                sqlcode = """
                UPDATE public.skill_training
                SET
                sk_id = %s,
                tr_id = %s,
                skill_training_delete_ind = %s
                WHERE concat(public.skill_training.sk_id,public.skill_training.tr_id) = %s
                """
                to_delete = bool(sktraining_remove) #checking asn_remove value (either true or false)
                values = [skilldropdown, trainingdropdown, to_delete, f'{sktraining_id}']
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "Skill's training program details updated!"

                # QUERY RETURN IDS
                sql_returnid = """
                SELECT sk_id, tr_id
                FROM public.skill_training
                WHERE concat(public.skill_training.sk_id,public.skill_training.tr_id) = %s
                """
                values_returnid = [f'{sktraining_id}']
                cols_returnid = ['sk_id', 'tr_id']
                returnidvalue = db.querydatafromdatabase(sql_returnid, values_returnid, cols_returnid)
                sk_id = int(returnidvalue['sk_id'][0])
                tr_id = int(returnidvalue['tr_id'][0])

                # IF ORIGIN PAGE IS SKILLPROF
                if pathname == '/skills/skillprofile/trainingskillprofile':
                    # REF OKAY BUTTON TO SKILLPROF
                    okay_href = f'/skills/skillprofile?mode=edit&id={sk_id}'
                # ELIF ORIGIN PAGE IS TRAININGPROF
                elif pathname == '/trainings/trainingprofile/trainingskillprofile':
                    # REF OKAY BUTTON TO TRAININGPROF
                    okay_href = f'/trainings/trainingprofile?mode=edit&id={tr_id}'

            else:
                raise PreventUpdate #can be a custom url error message
            
    elif eventid == 'skilltraining_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]