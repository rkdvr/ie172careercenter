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
        html.H2("Frequently Asked Questions"),
        html.Br(),
        html.H4("Employees"),
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    "YES, just search for the employee and click the Edit or Delete button to do so. Make sure to save your changes.", 
                    title="Can employee information still be edited or deleted after it's already been saved?"
                ),
                dbc.AccordionItem(
                    "NO, an employee can only be assigned one job at a time.", 
                    title="Can an employee have multiple jobs at once?"
                ),
                dbc.AccordionItem(
                    "NO, but they can change departments depending on the job they are currently assigned to.", 
                    title="Can an employee belong to multiple departments at once?"
                ),
                dbc.AccordionItem(
                    "An employee can register for and attend multiple trainings, given that these trainings are not scheduled at the same time.", 
                    title="Can an employee participate in multiple trainings at once?"
                ),
                dbc.AccordionItem(
                    "As soon as the employee finishes a particular training, their new skills and level gained from the session will be registered.", 
                    title="When can an employee improve their skill level?"
                )
            ],
            start_collapsed=True,
        ),
        html.Br(),
        html.H4("Jobs"),
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    "YES, just search for the job and click the Edit or Delete button to do so. Make sure to save your changes.", 
                    title="Can a job still be edited or deleted after it’s already been saved?"
                ),
                dbc.AccordionItem(
                    "NO, because one job posting is equivalent to one slot. For jobs requiring more than one employee, there will be more than one job posting for it.", 
                    title="Can multiple employees be assigned to a job?"
                ),
                dbc.AccordionItem(
                    "YES, a job can require more than just one skill. For example, a Project Manager can require the employee to be skilled in Basic Programming and Adobe CC to be an eligible candidate.", 
                    title="Can a job require many skills?"
                ),
                dbc.AccordionItem(
                    "YES, although to increase their chances of being assigned to a job, their skills must match the job requirements or better.", 
                    title="Can an employee still apply even if their skills don’t match the skills requirements of the job?"
                ),
                dbc.AccordionItem(
                    "YES, employees are allowed to do so. The department an employee is affiliated with will depend on the job they are assigned to. While they are not assigned to a job yet, their department will remain “Unassigned”.", 
                    title="Can an employee apply for a job in a different department?"
                ),
                dbc.AccordionItem(
                    "NO, only jobs that are hiring can accept applications.", 
                    title="Can I submit an employee application for a job that is no longer hiring?"
                )
            ],
            start_collapsed=True,
        ),
        html.Br(),
        html.H4("Training and Skills"),
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    "YES, just search for the training and click the Edit or Delete button to do so. Make sure to save your changes.", 
                    title="Can a training program still be edited or deleted after it’s already been saved?"
                ),
                dbc.AccordionItem(
                    "Employees who successfully complete the training program will gain the expected skills and skill level. Those who sign up for the program but are unable to complete it will not be able to gain the skills.", 
                    title="What can employees gain from completing a training program?"
                ),
                dbc.AccordionItem(
                    "YES, employees can gain multiple skills from one training program. For example, employees that completed the Advanced Programming Training are expected to gain both front-end and back-end development skills.", 
                    title="Can employees gain more than one skill from a training program?"
                ),
                dbc.AccordionItem(
                    "NO, there is no limit to the number of participants for each training.", 
                    title="Is there a limit to the number of employees that sign up for a training program?"
                ),
                dbc.AccordionItem(
                    "All employees can apply for any of the training programs.", 
                    title="Who can apply for the training programs?"
                ),
                dbc.AccordionItem(
                    "The level of the skills gained is dependent on the training program. For example, employees that have completed the Basic UX Training and the Advanced UX Training will both gain Figma skills but of different levels.", 
                    title="What is the expected level of skills that employees gain from completing a training program?"
                )
            ],
            start_collapsed=True,
        ),
        html.Br(),
        html.Span(
                "Contact the leila, cola, irene, and erika if you need assistance!",
                style={'font-style':'italic'}
        )
    ]
)

