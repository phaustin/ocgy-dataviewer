# -*- coding: utf-8 -*-

# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/
# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# mouse-over or 'hover' behavior is based on https://dash.plotly.com/interactive-graphing
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line
# Mapmaking code initially learned from https://plotly.com/python/mapbox-layers/.


from flask import Flask
from os import environ

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotting as plot

#initial settings for the plots
initial_cruise = 'GIPY0405'
initial_y_range = [0, 500]
initial_x_range = 'default'


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get('JUPYTERHUB_SERVICE_PREFIX', '/'),
    external_stylesheets=external_stylesheets
)

app.layout = html.Div([
    dcc.Markdown('''
        ### EOSC 372 GEOTRACES Assignment
        
        #### Instructions  
        
        - Hover over a station (dots on the map) to plot the corresponding temperature, salinity, nitrate, and iron profiles in blue.
        - Click on a station to plot its depth profiles.
        - To remove profiles, click again on the stations's dot on the map.  
        - The cruise can be changed with radiobuttons.
        - Mouse wheel zooms within the map.  
        - Use the slider to the left of the profiles to constrain the depth axis. Drag the top-most handle down, or the bottom-most handle up.
        - Adjust the x-axis range with radiobuttons.      
        - To save all profiles as one PNG image, click the "camera" icon that appears upper-right of plots when mouse pointer is over the profile plots.   

        ----------
        '''),

# plot with the map of cruise stations
    html.Div([
        dcc.Graph(
            id='map',
            config={
                'staticPlot': False,  # True, False
                'scrollZoom': True,  # True, False
                'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                'showTips': True,  # True, False
                'displayModeBar': False,  # True, False, 'hover'
                'watermark': True,
                'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d'],
            },
            clear_on_unhover = True, #clears hover plots when cursor isn't over the station
        )
    ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 20', 'vertical-align': 'middle', 'margin-bottom': 30, 'margin-right': 50, 'margin-left': 20}),


    # slider or checklist details at https://dash.plotly.com/dash-core-components
    # checkboxes can be lumped together but then logic in "update_graph" is messier.
    # Content can be delivered using html, but markdown is simpler.
    html.Div([

        # choose the cruise
        dcc.Markdown('''
        **Select Cruise**
        '''),

        dcc.RadioItems( #radiobuttons to choose the current cruise
            id='cruise',
            options=[
                {'label': 'GIPY04 and GIPY05', 'value': 'GIPY0405'},
                {'label': 'GA03', 'value': 'GA03'},
                {'label': 'GP02', 'value': 'GP02'}
            ],
            value=initial_cruise,
            style={"margin-bottom": "30px"}
        ),


        dcc.Markdown('''
            **Select x-axis fit**
        '''),
        dcc.RadioItems( #radiobuttons to select either a default x-axis range, or to fit to the data
            id='x_range',
            options=[
                {'label': 'default', 'value': 'default'},
                {'label': 'fit to data', 'value': 'fitted'},
            ],
            value=initial_x_range
        ),

    ], style={'width': '40%', 'display': 'inline-block', 'vertical-align': 'middle'}),

    html.Div([
        dcc.Markdown('''
            **Depth (m)**
        '''),
    ], style={'display': 'inline-block', 'width': '5%', 'vertical-align': 'middle', 'textAlign': 'center'}),

    html.Div([
        dcc.RangeSlider(
            # slider to select the y-axis range
            # range slider documentation: https://dash.plotly.com/dash-core-components/rangeslider
            # note: I couldn't find a way to put the "max" value on the bottom of the slider (to flip the slider vertically)
            # so I made the slider go from -500 to 0, and I take the absolute value of the range later
            id='y_range',
            min=-500,
            max=0,
            step=0.5,
            #adding ticks to the slider without having labels
            marks={
                0: '', -100: '', -200: '', -300: '', -400: '', -500: '',
            },
            value=[-500, 0],
            vertical=True,
            verticalHeight=360
        )
    ], style={'display': 'inline-block', 'width': '2%', 'vertical-align': 'middle'}),

    html.Div([
        # the graph of subplots which show depth profiles for different parameters
        dcc.Graph(
            id='profiles',
            config={
                'staticPlot': False,  # True, False
                'scrollZoom': False,  # True, False
                'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                'showTips': True,  # True, False
                'displayModeBar': 'hover',  # True, False, 'hover'
                'watermark': False,
                'modeBarButtonsToRemove': ['resetAxis', 'pan2d', 'resetScale2d', 'select2d', 'lasso2d', 'zoom2d',
                                           'zoomIn2d', 'zoomOut2d', 'hoverCompareCartesian', 'hoverClosestCartesian',
                                           'autoScale2d'],
            }
        ),
    ], style={'display': 'inline-block', 'width': '93%', 'vertical-align': 'middle', 'margin-bottom': '50px'}),

    dcc.Markdown('''
            *Density, Sigma0, is potential density anomaly, or potential density minus 1000 kg/m\u00B3. [Reference](http://www.teos-10.org/pubs/gsw/html/gsw_sigma0.html).
            '''),
    dcc.Markdown('''
        ----

        ### Attributions
 
        - Code by J. Byer for UBC's [OCESE project](https://www.eoas.ubc.ca/education/current-major-initiatives/ocese).
        - Oceanography Data from: Schlitzer, R., Anderson, R. F., Masferrer Dodas, E, et al., The GEOTRACES Intermediate Data Product 2017, Chem. Geol. (2018), https://doi.org/10.1016/j.chemgeo.2018.05.040.
        - Potential density anomaly (Sigma_0) calculated from salinity and temperature data using [The Gibbs SeaWater Oceanographic Toolbox of TEOS-10](http://www.teos-10.org/pubs/gsw/html/gsw_contents.html).

        ''')
], style={'width': '1000px'})



#using the plotting file to plot the figures

#initialize the map and the depth profiles
fig_map = plot.initialize_map(initial_cruise)
fig_profiles = plot.initialize_profiles(initial_cruise, initial_x_range, initial_y_range)

#Suplot graph
@app.callback(
    Output(component_id='profiles', component_property='figure'),
    Input(component_id='map', component_property='hoverData'),
    Input(component_id='map', component_property='clickData'),
    Input(component_id='cruise', component_property='value'),
    Input(component_id='x_range', component_property='value'),
    Input(component_id='y_range', component_property='value')
)
def update_profiles(hov_data, click_data, cruise, x_range, y_range):
    y_range[0] = abs(y_range[0])
    y_range[1] = abs(y_range[1])
    # if the callback that was triggered was the cruise changing, we switch profiles (switch cruises)
    # otherwise, we update the profiles for the current cruise
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        fig = plot.switch_profiles(click_data, cruise, fig_profiles, x_range, y_range)
    elif (dash.callback_context.triggered[0]['prop_id'] == 'map.clickData'):
        fig = plot.update_profiles(hov_data, click_data, cruise, fig_profiles, x_range, y_range)
    else:
        fig = plot.update_profiles(hov_data, None, cruise, fig_profiles, x_range, y_range)
    return fig



# The callback function with it's app.callback wrapper.
@app.callback(
    Output('map', 'figure'),
    Input('cruise', 'value'),
    Input('map', 'hoverData'),
    Input('map', 'clickData'),
    Input('map', 'figure')
)
def update_map(cruise, hov_data, click_data, figure_data):
    # switch map is called when we switch cruises, update map is called for other updates.
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        fig = plot.switch_map(cruise, fig_map)
    elif (dash.callback_context.triggered[0]['prop_id'] == 'map.clickData'):
        fig = plot.update_map(hov_data, click_data, figure_data, cruise, fig_map)
    else:
        fig = plot.update_map(hov_data, None, figure_data, cruise, fig_map)
    return fig



if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
