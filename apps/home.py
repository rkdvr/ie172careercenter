from dash import html
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container

# store the layout objects into a variable named layout
layout = html.Div (
    [
        html.Div(
            dbc.Container(
                [
                    html.H1('Hello 👋', className="display-3"),
                    html.P(
                        "Company ABC is a manufacturing company that holds multiple ad hoc projects," 
                        " creating new job opportunities for its employees.",
                        className="lead",
                    ),
                    html.P(
                        "Given its fast-paced and dynamic environment, the Career Management System" 
                        " supports its human resource and learning management activities for ABC managers in their day-to-day work.",
                        className="lead",
                    ),
                    html.Hr(className="my-2"),
                    html.P(
                        "For any assistance, contact the following:"
                    ),
                    html.P(
                        "leila (leilacrisostomo12@gmail.com), cola (nicoleannecobarrubias@gmail.com), irene (airenemutuc@gmail.com), and erika (erikaumalidevera@gmail.com)"
                    ),
                ],
                fluid=True,
                className="py-3",
            ),
            className="p-3 bg-light rounded-3",
        ),
        html.Iframe(src="https://www.youtube.com/embed/iMP6QUOlRBc?controls=0&autoplay=1&loop=1" , 
        title="", width='1080', height="630", allow='allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share'),
    ]
)

# layout = html.Div(
#     [
#         html.H1('Hello 👋'),
#         html.Hr(),
#         html.Div(
#             [
#                 html.H5( # span is a container for text
#                     "Company ABC is a manufacturing company that holds multiple ad hoc projects, creating new job opportunities for its employees."
#                 ),
#                 html.H5(
#                     "Given its fast-paced and dynamic environment, the Career Management System supports its human resource and learning management" 
#                 ),
#                 html.H5(
#                     "activities for ABC managers in their day-to-day work."
#                 ),
#                 html.Br(),
#                 html.Br(),
#                 html.Span(
#                 "Contact the leila, cola, irene, and erika if you need assistance!",
#                 style={'font-style':'italic'}
#                 )
#             ]
#         ),
#         html.Div(
#             jumbotron
#         )
#     ]
# )

