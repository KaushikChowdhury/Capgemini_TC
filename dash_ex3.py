import base64
import datetime
import io
import plotly.graph_objs as go
import cufflinks as cf

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

pp_graph = dcc.Graph(id='pp-graph1')

def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df
	

app.layout = html.Div(
    className="row",
    children=[ 
    html.H3("EDA  Web-Application using Dash", 
            style={'textAlign': 'center', 'color': '#0000A0'}),     
    html.Hr(),
    html.H5("Upload Files"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False),
    html.Br(),
    html.Div(id='output-data-upload'),
    pp_graph       
])

@app.callback(Output('output-data-upload', 'children'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])

def update_table(contents, filename):
    table = html.Div()
    if contents:
        df = parse_data(contents, filename)
        des_df = df.describe(include="all").reset_index()
        percent_missing = (df.isnull().sum() * 100 / len(df))
        miss_df = pd.DataFrame({'Column_Name': df.columns,'Percent_Missing': percent_missing}).reset_index(drop = True)
        table = html.Div([
        html.H4("Data Statistics for the Uploaded File Name:  {}".format(filename)),
		html.H6('Number of Columns: {} and Number of Rows: {}'.format(df.shape[0], df.shape[1])),
		html.H6('Number of Categorical Columns : {}'.format(df.select_dtypes(include=np.object).columns.tolist())),
		html.H6('Number of Numerical Columns : {}'. format(df.select_dtypes(include=np.number).columns.tolist())),
		html.H6('Number of Boolean Columns : {}'. format(df.select_dtypes(include=np.bool).columns.tolist())),
		html.H6('Missing Value Table: '),
		dash_table.DataTable(
            data = miss_df.to_dict('rows'),
            columns=[{'name': i, 'id': i} for i in miss_df.columns],
            style_cell={'textAlign': 'left'}),
		html.H6('Summary Statistics Table: '),
		dash_table.DataTable(
            data=des_df.to_dict('rows'),
            columns=[{'name': i, 'id': i} for i in des_df.columns],
            style_cell={'textAlign': 'left'}
                ),
        ])     
    return table

@app.callback(Output('pp-graph1', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])

def update_graph(contents, filename):
    fig = {
        'layout': go.Layout(
            plot_bgcolor=colors["graphBackground"],
            paper_bgcolor=colors["graphBackground"])
    }

    if contents:
        #contents = contents[0]
        #filename = filename[0]
        df = parse_data(contents, filename)
        #df = df.set_index(df.columns[0])
        col1 = df.select_dtypes(include = np.number).columns.tolist()[0]
        col2 = df.select_dtypes(include = np.number).columns.tolist()[1]
        
        data = [go.Bar(x=df[col1], y=df[col2])]        
        layout = go.Layout(title='Sample bi-variate Plot')
    else:
        data = [go.Bar(x=[0,0], y=[0,0], name='sample data')]
        layout = go.Layout(title='sample graph')
    return {'data': data, 'layout': layout}


if __name__ == '__main__':
    app.run_server(debug=True)