#!/usr/bin/env python
# coding: utf-8

import io
import os
import base64
import tempfile
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pyreadstat
import pandas as pd
from DDICDI_converter import generate_complete_jsonld
from spss_import import read_sav, create_variable_view
from app_content import markdown_text, colors, style_dict, table_style, header_dict


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
app.title = "SAV File Viewer"

# Define the navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("DDI-CDI Sample Generator - Wide Datafile", href="#")),
    ],
    brand="SAV File Viewer",
    brand_href="#",
    color="dark",
    dark=True,
)

app.layout = dbc.Container([
    navbar,
    dbc.Row([
        dbc.Col([
            html.Br(),
            dcc.Upload(
                id='upload-data',
                children=dbc.Button('Import SPSS', color="primary", className="mr-1"),
                multiple=False,
                accept=".sav"
            ),
            html.Br(),

            # Add a button to switch between tables
            dbc.Button("Switch Table", id="table-switch-button", color="primary", className="mr-1"),

            html.Br(),

            # Create two separate columns for the tables and wrap them in a Row
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-table1",
                        type="default",
                        children=[
                            dash_table.DataTable(
                                id='table1',
                                columns=[],
                                # When setting column data, set 'editable': True for columns you want editable
                                data=[],
                                style_table=table_style,
                                style_header=header_dict,
                                style_cell=style_dict
                            )

                        ]
                    ),
                ], id="table1-col"),
                dbc.Col([
                    dcc.Loading(
                        id="loading-table2",
                        type="default",
                        children=[
                            dash_table.DataTable(
                                id='table2',
                                columns=[{"name": "Role", "id": "select_column", "type": "text",
                                          "presentation": "markdown"}] + [],

                                data=[],
                                editable=False,  # Allow content to be editable
                                row_selectable="multi",  # Allow multiple rows to be selected
                                selected_rows=[],
                                style_table=table_style,
                                style_header=header_dict,
                                style_cell=style_dict
                            ),
                        ]
                    ),
                ], id="table2-col", style={'display': 'none'}),  # Initially, hide the second table
            ]),

            html.Br(),
            dbc.Button('Download JSON-LD', id='btn-download', color="success", className="mr-1",
                       style={'display': 'none'}),
            dcc.Download(id='download-jsonld'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Pre(
                        id='json-ld-output',
                        style={
                            'whiteSpace': 'pre',
                            'wordBreak': 'break-all',
                            'color': colors['text'],
                            'backgroundColor': colors['background'],
                            'marginTop': '10px',
                            'maxHeight': '300px',
                            'overflowY': 'scroll',
                            'fontSize': '14px',
                        }
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Markdown(markdown_text),
                            style={
                                'overflowY': 'scroll',  # Add scroll if content is too long
                                'height': '400px',  # Adjust based on your requirement
                                'border': '1px solid #ccc',  # Optional: Add a border for better visibility
                                'padding': '10px',  # Add some padding
                                'fontSize': '14px',  # Adjust font size if needed
                            }
                        )
                    ])
                ], width=6)

            ]),
        ])
    ])
], fluid=True)

# ... [The initial imports and other code remains unchanged]

def style_data_conditional(df):
    style_data_conditional = []
    for col in df.columns:
        if df[col].dtype == "object":
            style_data_conditional.append({
                'if': {'column_id': col},
                'textAlign': 'left',
                'maxWidth': '150px',
                'whiteSpace': 'normal',
                'height': 'auto',
            })
    return style_data_conditional
# Define callbacks
@app.callback(
    [Output('table1', 'data'),
     Output('table1', 'columns'),
     Output('table1', 'style_data_conditional'),
     Output('table2', 'data'),
     Output('table2', 'columns'),
     Output('table2', 'style_data_conditional'),
     Output('json-ld-output', 'children'),
     Output('btn-download', 'style')],
    [Input('upload-data', 'contents'),
     Input('table2', 'selected_rows')],
    [State('upload-data', 'filename'),
     State('table2', 'data')]
)
def combined_callback(contents, selected_rows, filename, table2_data):
    print("Callback activated!")

    # Check if any row is selected
    if selected_rows:
        for row_index in selected_rows:
            selected_row_data = table2_data[row_index]
            if "name" in selected_row_data:
                print(selected_row_data["name"])

    if not contents:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    tmp_fd, tmp_filename = tempfile.mkstemp(suffix='.sav')
    with os.fdopen(tmp_fd, 'wb') as tmp_file:
        tmp_file.write(decoded)

    try:
        df, df_meta = read_sav(tmp_filename)
        df2 = create_variable_view(df_meta)
        df = df.head(10)
        columns1 = [{"name": i, "id": i} for i in df.columns]
        columns2 = [{"name": i, "id": i} for i in df2.columns]

        conditional_styles1 = style_data_conditional(df)
        conditional_styles2 = style_data_conditional(df2)

        jsonld_data = generate_complete_jsonld(df, df_meta, filename)
        return (df.to_dict('records'), columns1, conditional_styles1, df2.to_dict('records'),
                columns2, conditional_styles2, jsonld_data, {'display': 'block'})

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return [], [], [], [], [], [], f"An error occurred while processing the file.", {'display': 'none'}

    finally:
        os.remove(tmp_filename)


@app.callback(
    [Output("table1-col", "style"),
     Output("table2-col", "style")],
    [Input("table-switch-button", "n_clicks")],
    [State("table1-col", "style"),
     State("table2-col", "style")]
)
def switch_table(n_clicks, style1, style2):
    if n_clicks is None:
        return style1, style2

    if n_clicks % 2 == 0:
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}


@app.callback(
    Output('download-jsonld', 'data'),
    [Input('btn-download', 'n_clicks')],
    [State('json-ld-output', 'children'),
     State('upload-data', 'filename')]
)
def download_jsonld(n_clicks, jsonld_data, filename):
    if n_clicks is None or filename is None or jsonld_data is None:
        raise dash.exceptions.PreventUpdate

    download_filename = os.path.splitext(filename)[0] + '.jsonld'
    return dict(content=jsonld_data, filename=download_filename, type='text/json')


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
