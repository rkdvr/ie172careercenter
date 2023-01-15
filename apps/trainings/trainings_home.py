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

trainingsreport = [
    dbc.CardBody(
        [
            html.H2("# Training Programs", id='training_stat'),
            # html.P('Developed in the Current Year'),
        ],
        style={'text-align': 'center'}
    ),
    html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button("View Trainings and Skills Report", id="trainings_btn", n_clicks=0, color="light"),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle("Trainings Report of Current Year")),
                                    dbc.ModalBody(
                                        "This will contain the table for training programs.", 
                                        id='currenttraining_list'
                                    ),
                                ],
                                id="trainings_modal",
                                # size="xl",
                                fullscreen = True,
                                is_open=False,
                            ),
                        ],
                        className="d-grid gap-2",
                    ),
                ],
            )
        ],
    )
]

layout = html.Div(
    [
        html.H2("Trainings"),
        html.Hr(),
        #TRAININGS REPORT
        dbc.Row(
            html.Div(
                dbc.Card(trainingsreport, color="dark", outline=True), #outline=True
                className="w-20"
            ),
            
        ),
        html.Br(),
        html.Br(),
        # SEARCH BARS
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        type="text", id="training_filter", placeholder="🔍 Search a Training"
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.Input(
                        type="text", id="skill_filter", placeholder="🔍 Search a Skill"
                    ),
                    width=6,
                ),
            ]
        ),
        html.Br(),
        html.Br(),
        html.Div(
                "This will contain the table for all trainings.",
                id='trainings_list'
        ),
        html.Br(),
        html.Div(
            [
                dbc.Button("Add New Training", id="new_training", n_clicks=0, color= 'warning', href='/trainings/trainingprofile?mode=add'),  
            ]
        )
    ]
)

@app.callback(
    [
        Output('trainings_list','children'),
        Output('currenttraining_list', 'children'),
        Output('training_stat', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('training_filter', 'value'),
        Input('skill_filter', 'value'),
    ]
)

def loadtraininglist (pathname, searchtraining, searchskill):
    if pathname == '/trainings':

        #LOAD TRAINING LIST----------------------------------------------------------------------
        sql ="""
        SELECT tr_n, tr_s, tr_ed, STRING_AGG(sk_n,', '), trainings.tr_id
        FROM trainings
            FULL OUTER JOIN skill_training on skill_training.tr_id = trainings.tr_id
            FULL OUTER JOIN skills on skills.sk_id = skill_training.sk_id
        WHERE training_delete_ind = false
        """
        values = []
        colnames = ['Training Name', 'Start Date', 'End Date', 'Skills Gained','ID']

        # BEFORE ADDING QUERY IN PGADMIN, ADD FILTER
        if searchtraining:
            # We use the operator ILIKE for pattern-matching
            sql += "AND tr_n ILIKE %s"
            values += [f'%{searchtraining}%']
        
        sql += "GROUP BY tr_n, tr_s, tr_ed, trainings.tr_id"

        if searchskill:
            sql += " HAVING STRING_AGG(sk_n,', ') ILIKE %s"
            values += [f'%{searchskill}%']

        # RUN MODIFY DB FORMULA
        traininglist = db.querydatafromdatabase(sql, values, colnames)

        # IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if traininglist.shape[0]:
            
            #CREATE EDIT/DELETE BUTTONS COLUMN
            buttons =[]
            for tr_id in traininglist['ID']:
                buttons += [
                    dbc.Button(
                        '⚙️ Edit or Remove', 
                        href=f"/trainings/trainingprofile?mode=edit&id={tr_id}",
                        size='sm',
                        color='dark'
                    )
                ]
            
            #ADD BUTTONS TO traininglist TABLE
            traininglist['Action'] = buttons
            #REMOVE ID COLUMN -> axis options: 1 - column, 0 - row
            traininglist.drop('ID', axis=1, inplace=True) 

            training_table = html.Div(
                dbc.Table.from_dataframe(
                    traininglist, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )
        # IF EMPTY, RAISE PROMPT
        else:
            training_table = "No records to display"
        
        #LOAD CURRENT TRAININGS LIST----------------------------------------------------------------------
        sql_currenttr ="""
        SELECT tr_n, tr_s, tr_ed, STRING_AGG(DISTINCT sk_n,', '), STRING_AGG(DISTINCT(CONCAT(employees.emp_fn,' ',employees.emp_ln)),', ')
        FROM trainings
            INNER JOIN skill_training on skill_training.tr_id = trainings.tr_id
            INNER JOIN skills on skills.sk_id = skill_training.sk_id
            INNER JOIN employee_training on employee_training.tr_id = trainings.tr_id
            INNER JOIN employees on employees.emp_id = employee_training.emp_id
        WHERE DATE_PART('year', tr_s) = DATE_PART('year',current_date)
            AND training_delete_ind = false
            GROUP BY tr_n, tr_s, tr_ed
        """
        values_currenttr = []
        colnames_currenttr = ['Training Name', 'Start Date', 'End Date', 'Skills', 'Employees']
        currenttrainings = db.querydatafromdatabase(sql_currenttr, values_currenttr, colnames_currenttr)

        # IF THERE ARE VALUES, CREATE TABLE AND ADD TO INTERFACE
        if currenttrainings.shape[0]:

            current_trainings = html.Div(
                dbc.Table.from_dataframe(
                    currenttrainings, 
                    striped=True, 
                    bordered=True, 
                    hover=True, 
                    size='sm',
                    style={'text-align': 'center'}
                )
            )
        # IF EMPTY, RAISE PROMPT
        else:
            current_trainings = "No records to display"

        #LOAD TRAINING STAT----------------------------------------------------------------------
        sql_trstat ="""
        SELECT COUNT(*)
        FROM trainings
            WHERE DATE_PART('year', tr_s) = DATE_PART('year',current_date)
            AND training_delete_ind = false
        """
        values_trstat = []
        colnames_trstat = ['Training Programs']
        currenttrainings_count = db.querydatafromdatabase(sql_trstat, values_trstat, colnames_trstat)

        if currenttrainings_count.shape[0]:
            current_training_stat = currenttrainings_count['Training Programs'][0]
        else:
            current_training_stat = '0'
        
        current_training_card = f'📚 {current_training_stat} Trainings Developed This Year'

    else:
        raise PreventUpdate

    return [training_table, current_trainings, current_training_card] 

# OPEN REPORTS
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

app.callback(
    Output("trainings_modal", "is_open"),
    Input("trainings_btn", "n_clicks"),
    State("trainings_modal", "is_open"),
)(toggle_modal)
app.callback(
    Output("participants_modal", "is_open"),
    Input("participants_btn", "n_clicks"),
    State("participants_modal", "is_open"),
)(toggle_modal)