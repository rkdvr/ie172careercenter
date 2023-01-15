import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.exceptions import PreventUpdate
import pandas as pd
# Let us import the app object in case we need to define
# callbacks here
from app import app

layout = html.Div(
    [
        html.H2("🤔 How to Use Career Center"),
        html.Br(),
        dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    [
                        html.Div(
                            [
                                html.H5("👥 Employees", className="mb-1"),
                            ],
                            className="d-flex w-100 justify-content-between",
                        ),
                        html.P(
                            """The Employees page allows managers to browse through the table of all employees and add, 
                            update, and delete information as needed. This page is where a manager can see an employee's 
                            basic information, job history, skills, and trainings attended.
                            """, 
                            className="mb-1"
                        ),
                    ]
                ),
                dbc.ListGroupItem(
                    [
                        html.Div(
                            [
                                html.H5(
                                    "💻 Jobs", className="mb-1"
                                ),
                            ],
                            className="d-flex w-100 justify-content-between",
                        ),
                        html.P(
                            """The jobs page allows managers to browse through the table of all jobs and add, 
                            update, and delete information as needed. This is also where specific job information 
                            such as the description, skills it requires, and assigned employees (if any) can be viewed.
                            """, 
                            className="mb-1"
                        ),
                        html.P(
                            """There is a Job Openings page that shows all jobs currently hiring. A manager can post a job 
                            opening on this site and also upload an employee's application to a job through here.
                            """, 
                            className="mb-1"
                        ),
                    ]
                ),
                dbc.ListGroupItem(
                    [
                        html.Div(
                            [
                                html.H5(
                                    "✏️ Trainings and Skills", className="mb-1"
                                ),
                            ],
                            className="d-flex w-100 justify-content-between",
                        ),
                        html.P(
                            """The trainings page allows managers to browse through the table of all trainings 
                            and skills and add, update, and delete information as needed. 
                            """, 
                            className="mb-1"
                        ),
                        html.P(
                            """Through this page, a manager can manage the specific skills acquired from the training, 
                            as well as the employee who will be participating in the program.
                            """, 
                            className="mb-1"
                        ),
                    ]
                ),
            ]
        )
    ]
)

