# Usual Dash dependencies
from dash import html
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
from dash_bootstrap_components._components.Container import Container

# # CSS Styling for the NavLink components
addpage_style = {
    'font-style':'italic',
    'color':'#006FB9'
}

BRAND_LOGO = "https://cdn-icons-png.flaticon.com/512/1086/1086474.png"

# navbar = dbc.Navbar(
#     [
#         #for the logo and brand
#         html.A(
#             dbc.NavbarBrand("Career Center", className="ml-2", 
#                 style={'margin-right': '2em', "margin-left": "4em"}),
#             href="/home",
#         ),
#         dbc.NavLink("Home", href="/home", style=navlink_style),
#         dbc.NavLink("Employees", href="/employees", style=navlink_style),
#         dbc.NavLink("Jobs", href="/jobs", style=navlink_style),
#         dbc.NavLink("Trainings", href="/trainings", style=navlink_style),      
#         dbc.NavLink("Profile", href="/profile", style=navlink_style),      
#         dbc.NavLink("Help", href="/help", style=navlink_style),              
#     ],
#     color= '#437FC7',
#     dark=True
# )

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink("Home", href="/home")
        ),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Directory", href="/employees"),
                dbc.DropdownMenuItem("+ Add New Employee", href="/employees/employeeprofile?mode=add", style=addpage_style),
            ],
            nav=True,
            in_navbar=True,
            label="Employees",
        ),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Jobs List", href="/jobs"),
                dbc.DropdownMenuItem("Job Openings", href="/jobopen"),
                dbc.DropdownMenuItem("+ Add New Job", href="/jobs/jobprofile?mode=add", style=addpage_style)
            ],
            nav=True,
            in_navbar=True,
            label="Jobs",
        ),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Trainings", href="/trainings"),
                dbc.DropdownMenuItem("Skill Bank", href="/skills"),
                dbc.DropdownMenuItem("+ Add New Training", href="/trainings/trainingprofile?mode=add", style=addpage_style)
            ],
            nav=True,
            in_navbar=True,
            label="Skills & Trainings",
        ),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("How to use Career Center", href="/instructions"),
                dbc.DropdownMenuItem("FAQs", href="/faqs"),
            ],
            nav=True,
            in_navbar=True,
            label="Help",
        ),
        dbc.NavItem(dbc.NavLink("Log Out", href="/logout"))
    ],
    brand="📶 Career Center",
    brand_href="/home",
    color="#006FB9",
    dark=True,
)

#0d4263  -darker
#006FB9
# search_bar = dbc.Row(
#     [
#         dbc.NavItem(
#             dbc.Button(
#                 "Home", href="/home", color=None
#             )
#         ),
#         dbc.NavItem(
#              dbc.DropdownMenu(
#                 children=[
#                     dbc.DropdownMenuItem("Directory", href="/employees"),
#                     dbc.DropdownMenuItem("+ Add New Employee", href="/employees/employeeprofile?mode=add", style=addpage_style),
#                 ],
#                 label="Employees",
#             ),
#         ),
#         dbc.NavItem(
#             dbc.DropdownMenu(
#                 children=[
#                     dbc.DropdownMenuItem("Jobs List", href="/jobs"),
#                     dbc.DropdownMenuItem("Job Openings", href="/jobopen"),
#                     dbc.DropdownMenuItem("+ Add New Job", href="/jobs/jobprofile?mode=add", style=addpage_style)
#                 ],
#                 label="Jobs",
#             ),
#         ),
#         dbc.NavItem(
#             dbc.DropdownMenu(
#                 children=[
#                     dbc.DropdownMenuItem("Ongoing Trainings", href="/trainings"),
#                     dbc.DropdownMenuItem("Skill Bank", href="/skills"),
#                     dbc.DropdownMenuItem("+ Add New Training", href="/trainings/trainingprofile?mode=add", style=addpage_style)
#                 ],
#                 label="Skills & Trainings",
#             ),
#         ),
#         dbc.NavItem(
#             dbc.DropdownMenu(
#                 children=[
#                     dbc.DropdownMenuItem("How to use Career Center", href="/instructions"),
#                     dbc.DropdownMenuItem("FAQs", href="/faqs"),
#                 ],
#                 label="Help",
#             ),
#         ),
#         dbc.NavItem(
#             dbc.Button(
#                 "Log Out", href="/logout", color=None
#             ),
#         )
#     ],
#     className="g-0 ms-auto flex-nowrap", #mt-3 mt-md-0",
#     align="center",
# )

# navbar = dbc.Navbar(
#     dbc.Container(
#         [
#             html.A(
#                 # Use row and col to control vertical alignment of logo / brand
#                 dbc.Row(
#                     [
#                         dbc.Col(html.Img(src=BRAND_LOGO, height="30px")),
#                         dbc.Col(dbc.NavbarBrand("Career Center", className="ms-2")),
#                     ],
#                     align="center",
#                     className="g-0",
#                 ),
#                 href="https://plotly.com",
#                 style={"textDecoration": "none"},
#             ),
#             dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
#             dbc.Collapse(
#                 search_bar,
#                 id="navbar-collapse",
#                 is_open=False,
#                 navbar=True,
#                 style={'color': 'None'}
#             ),
#         ]
#     ),
#     color="#006FB9",
#     dark=True,
# )