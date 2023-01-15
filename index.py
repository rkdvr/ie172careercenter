# Dash related dependencies
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
# To open browser upon running your app
import webbrowser

# Importing your app definition from app.py so we can use it
from app import app
from apps import commonmodules as cm
from apps import home
from apps import signup, login
from apps.employees import employees_home, employee_prof, add_empjob, add_empskill, add_emptraining
from apps.jobs import jobs_home, job_profile, job_openings, job_newopen, job_applications, add_jobapp, add_jobskill
from apps.trainings import trainings_home, training_prof, skills_home, skill_profile, add_trskill
from apps.help import help_faqs, help_instructions

CONTENT_STYLE = {
    "margin-left": "1em",
    "margin-right": "1em",
    "padding": "1em 1em",
}

app.layout = html.Div(
    [
        # Location Variable -- contains details about the url
        dcc.Location(id='url', refresh=True),
        #adding navbar to layout
        
        # LOGIN DATA
        # 1) logout indicator, storage_type='session' means that data will be retained
        #  until browser/tab is closed (vs clearing data upon refresh)
        dcc.Store(id='sessionlogout', data=False, storage_type='session'),
        
        # 2) current_user_id -- stores user_id
        dcc.Store(id='currentuserid', data=-1, storage_type='session'),
        
        # 3) currentrole -- stores the role
        # we will not use them but if you have roles, you can use it
        dcc.Store(id='currentrole', data=-1, storage_type='session'),
        
        html.Div(
            cm.navbar,
            id='navbar_div'
        ),
        # Page Content -- Div that contains page layout
        html.Div(id='page-content', style=CONTENT_STYLE),
    ]
)

# if the URL changes, the content changes as well
@app.callback(
    [
        Output('page-content', 'children'),
        Output('navbar_div', 'style'),
        Output('sessionlogout', 'data'),
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
    ]
)

def displaypage(pathname, sessionlogout, currentuserid):
    
    #determines what element triggered the function
    ctx = dash.callback_context
    if ctx.triggered:
        # eventid = name of element that caused the trigger
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        # used to terminate function if no trigger
        raise PreventUpdate

    if eventid == 'url':
        print(currentuserid, pathname)
        if currentuserid < 0:
            if pathname in ['/']:
                returnlayout = login.layout
            elif pathname == '/signup':
                returnlayout = signup.layout
            else:
                returnlayout = '404: request not found'
            
        else:
            if pathname == '/logout': 
                returnlayout = login.layout
                sessionlogout = True
                
            elif pathname in ['/', '/home']:
                returnlayout = home.layout
                
           #EMPLOYEES
            elif pathname == '/employees': #DONE
                returnlayout = employees_home.layout
            elif pathname == '/employees/employeeprofile': #DONE
                returnlayout = employee_prof.layout
                #ASSIGNMENTS
            elif pathname == '/employees/employeeprofile/assignmentprofile':
                returnlayout = add_empjob.layout
                #EMP-SKILL
            elif pathname == '/employees/employeeprofile/skillrecord':
                returnlayout = add_empskill.layout
                #EMP-TRAINING
            elif pathname == '/employees/employeeprofile/participantprofile':
                returnlayout = add_emptraining.layout

            #JOBS
            elif pathname == '/jobs': #DONE
                returnlayout = jobs_home.layout
            elif pathname == '/jobs/jobprofile': #DONE
                returnlayout = job_profile.layout
                #ASSIGNMENTS
            elif pathname == '/jobs/jobprofile/assignmentprofile': 
                returnlayout = add_empjob.layout
                #JOB-SKILL
            elif pathname == '/jobs/jobprofile/jobskillprofile': 
                returnlayout = add_jobskill.layout

            #JOB OPENINGS
            elif pathname == '/jobopen': #DONE
                returnlayout = job_openings.layout
            elif pathname == '/jobopen/applications': #DONE
                returnlayout = job_applications.layout
                #APPLICATIONS
            elif pathname == '/jobopen/applications/applicantprofile': 
                returnlayout = add_jobapp.layout
            elif pathname == '/jobopen/jobnewopen': #DONE
                returnlayout = job_newopen.layout
            
            #TRAININGS
            elif pathname == '/trainings': #DONE
                returnlayout = trainings_home.layout
            elif pathname == '/trainings/trainingprofile': #DONE
                returnlayout = training_prof.layout
                #TRAINING-SKILL
            elif pathname == '/trainings/trainingprofile/trainingskillprofile':
                returnlayout = add_trskill.layout
                #EMP-TRAINING
            elif pathname == '/trainings/trainingprofile/participantprofile':
                returnlayout = add_emptraining.layout
            
            #SKILLS
            elif pathname == '/skills': #DONE
                returnlayout = skills_home.layout
            elif pathname == '/skills/skillprofile': #DONE
                returnlayout = skill_profile.layout
                #SKILL-TRAINING
            elif pathname == '/skills/skillprofile/trainingskillprofile':
                returnlayout = add_trskill.layout
            
            #HELP
            elif pathname == '/instructions':
                returnlayout = help_instructions.layout
            elif pathname == '/faqs':
                returnlayout = help_faqs.layout
                
            else:
                returnlayout = '404: request not found'
    else:
        raise PreventUpdate
    
    navbar_div = {'display':  'none' if sessionlogout else 'unset'}
    return [returnlayout, navbar_div, sessionlogout]

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run_server(debug=False)