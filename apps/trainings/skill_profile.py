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
                dcc.Store(id='skillprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2('Skill Details'),
        html.Hr(),
        #Skill Name--------------------------------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Skill Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="skillprof_name", placeholder="Enter skill name"
                    ),
                        width=4,
                ),
            ],
            className="mb-3",
        ),
        #Skill Description----------------------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Description", width=2),
                dbc.Col(
                    dbc.Textarea(className="mb-3", placeholder="Enter description here", id="skillprof_desc"),
                    width=4
                )
            ],
            className="mb-3",
        ),
        #Skill Category-----------------------------------------------------
        dbc.Row(
            [
                dbc.Label("Skill Category", width=2),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='skillctg_dropdown',
                            placeholder = 'Select Category',
                            clearable=True,
                            searchable=True,
                            options=[
                                {'label':'Functional Skills','value':'Functional Skills'},
                                {'label':'Managerial Skills','value':'Managerial Skills'},
                                {'label':'Methodological Skills','value':'Methodological Skills'},
                                {'label':'Technical Skills','value':'Technical Skills'}
                            ]
                        ), 
                        className="dash-bootstrap"
                    ),
                    width=4,
                ),
            ],
            className="m-3"
        ),
        html.Br(),
        #HIDDEN------------------------------------------------------------------------------------
        html.Div(
            [
                #TRAININGS
                html.H3('Training Programs'),
                dbc.Row(
                    "Insert table of training history here.",
                    id='skill_trainingprogram'
                ),
                html.Br(),
                html.Div(
                    [
                        dbc.Button("Add Training Program", id="add_sk_training", n_clicks=0, color= 'secondary'),
                    ]
                ), 
                html.Br(),
                #DELETE
                dbc.Row(           
                    [
                        dbc.Label("Delete Skill?", width=2, style={'color': 'red'}),
                        dbc.Col(
                            dbc.Checklist(
                                id='skill_removerecord',
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
            id='skill_editmode_div'
        ),

        #SUBMIT------------------------------------------------------------------------------------------
        dbc.Button("Submit", color= 'warning', id='skillprof_submitbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody('temp message', id='skillprof_feedbackmsg'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="skillprof_closebtn", className="ms-auto", n_clicks=0, color= 'warning'
                    )
                ),
            ],
            id="skillprof_modal",
            is_open=False,
        )  
    ]
)

# SUBMIT (INSERT AND UPDATE) PROCESS--------------------------------------------------------------------------------
@app.callback(
    [
        Output("skillprof_modal", "is_open"),
        Output("skillprof_feedbackmsg", "children"),
        Output("skillprof_closebtn", "href")
    ],
    [
        Input("skillprof_submitbtn", "n_clicks"),
        Input("skillprof_closebtn", "n_clicks"),
    ],
    [
        State('skillprof_name', 'value'),
        State('skillprof_desc', 'value'),
        State('skillctg_dropdown', 'value'),
        State('url', 'search'),
        State('skill_removerecord', 'value'),
    ]
)
def trainingprof_submitprocess(submitbtn, closebtn,
                        skillname, skilldesc, category,
                        search, skillremove): 

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
    if eventid == 'skillprof_submitbtn' and submitbtn:
        
        # OPEN MODAL
        openmodal = True

        inputs = [
            skillname, 
            skilldesc,
            category,
        ] 

        # IF INVALID INPUTS,
        if not all(inputs):
            # GIVE ERROR PROMPT
            feedbackmsg = "Please provide all inputs correctly."

        # ELIF VALID INPUTS
        else:
            # REF OKAY BUTTON TO SKILL HOME
            okay_href = '/skills'

            parsed = urlparse(search)
            mode = parse_qs(parsed.query)['mode'][0]
            
            # IF MODE IS ADD
            if mode == 'add':
                
                # SAVE TO DB
                sqlcode = """
                INSERT INTO skills(sk_n, sk_ds, sk_c)
                VALUES(%s, %s, %s)
                """
                values = [skillname, skilldesc, category]
                db.modifydatabase(sqlcode,values)

                # GIVE ADDED FEEDBACK
                feedbackmsg = "Skill Added!"

            # ELIF MODE IS EDIT
            elif mode == 'edit':
                sk_id = parse_qs(parsed.query)['id'][0]

                # UPDATE DB QUERY
                sqlcode = """
                UPDATE skills
                SET
                sk_n = %s,
                sk_ds = %s,
                sk_c = %s,
                skill_delete_ind = %s
                WHERE sk_id = %s
                """
                
                to_delete = bool(skillremove)
                
                values = [skillname, skilldesc, category, to_delete, sk_id]
                db.modifydatabase(sqlcode,values)

                # GIVE UPDATED FEEDBACK
                feedbackmsg = "Skill has been updated!"
            else:
                raise PreventUpdate #can be a custom URL ERROR MESSAGE

    # ELIF CLOSE BUTTON WAS CLICKED,
    elif eventid == 'skillprof_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate
    
    return [openmodal, feedbackmsg, okay_href]

# LOAD ELEMENTS UPON PAGE LOAD--------------------------------------------------------------------------------
@app.callback(
    [
        Output('skillprof_toload', 'data'),
        Output('skill_editmode_div', 'style'),
        Output('add_sk_training', 'href'),
        Output('skill_trainingprogram', 'children')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def triggereditmode (pathname, search):

    if pathname == '/skills/skillprofile':

        parsed = urlparse(search)
        mode = parse_qs(parsed.query)['mode'][0]        
        to_load = 1 if mode == 'edit' else 0 
        editelementsdiv = None if to_load else {'display': 'none'}

        #EMPTY VALUES IF ADD MODE
        sktraining_href = ""
        trainingprograms = ""

        # VALUES IF EDIT MODE
        if to_load:
            parsed = urlparse(search)
            sk_id = parse_qs(parsed.query)['id'][0]
            # ADD REFERENCE TO FORMS TO ADD TO JUNCTION TABLES
            sktraining_href = f"/skills/skillprofile/trainingskillprofile?mode=add&id={sk_id}"

            # LOAD SKILL-TRAINING CHILDREN--------------------------------------------------------
            sql_skilltr= """
			SELECT tr_n, tr_ds, tr_s, tr_ed, concat(skill_training.sk_id, skill_training.tr_id)
                FROM skills
                INNER JOIN skill_training on skill_training.sk_id = skills.sk_id
                INNER JOIN trainings on trainings.tr_id = skill_training.tr_id
            WHERE skills.sk_id = %s 
                AND skill_delete_ind = false
                AND training_delete_ind = false
				AND skill_training.skill_training_delete_ind = false
            """
            values_skilltr = [sk_id]
            colnames_skilltr = ['Training Name', 'Description', 'Start', 'End','ID']
            trainingprogsdf = db.querydatafromdatabase(sql_skilltr, values_skilltr, colnames_skilltr)

            if trainingprogsdf.shape[0]:
                # ADD A BUTTON PER ROW THAT CAN EDIT ITS CONTENTS
                buttons =[]
                for skilltr_id in trainingprogsdf['ID']:
                    buttons += [
                        dbc.Button(
                            '⚙️ Edit or Remove', 
                            href=f"/skills/skillprofile/trainingskillprofile?mode=edit&id={skilltr_id}",
                            size='sm',
                            color='dark'
                        )
                    ]
                
                # ADD COLUMN FOR EDIT BUTTONS
                trainingprogsdf['Action'] = buttons #add column named action containing the buttons
                trainingprogsdf.drop('ID', axis=1, inplace=True) #remove id col -> axis: 1 - column, 0 - row

                # LOAD TABLES
                trainingprograms = html.Div(
                    dbc.Table.from_dataframe(
                        trainingprogsdf, 
                        striped=True, 
                        bordered=True, 
                        hover=True, 
                        size='sm',
                        style={'text-align': 'center'}
                    )
                )
            else:
                # RAISE NULL PROMPT
                trainingprograms = "No records to display"

    else:
        raise PreventUpdate

    return [to_load, editelementsdiv, sktraining_href, trainingprograms]

#LOAD INFORMATION TO INTERFACE
@app.callback(
    [
        Output('skillprof_name', 'value'),
        Output('skillprof_desc', 'value'),
        Output('skillctg_dropdown', 'value'),
    ],
    [
        Input('skillprof_toload', 'modified_timestamp')
    ],
    [
        State('skillprof_toload', 'data'),
        State('url', 'search')
    ]
)
def loadskillinfo(timestamp, to_load, search):
    if to_load == 1:
        parsed = urlparse(search)
        sk_id = parse_qs(parsed.query)['id'][0] #the key is 'id' in URL       
        
        #1 QUERY DETAILS FROM DATABASE
        sql = """
        SELECT sk_n, sk_ds, sk_c
        FROM skills
        WHERE sk_id = %s
        """
        values =[sk_id]
        colnames =['skillname', 'skilldesc', 'skillcategory']
        df = db.querydatafromdatabase(sql, values, colnames) #df = dataframe

        #2 LOAD VALUES ON INTERFACE
        skillname = df['skillname'][0]
        skilldesc = df['skilldesc'][0]
        skillcategory = df['skillcategory'][0]

        return [skillname, skilldesc, skillcategory]

    else:
        raise PreventUpdate