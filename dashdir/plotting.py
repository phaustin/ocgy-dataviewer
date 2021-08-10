import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import station

# see Python routine "parse-csv.py" for the method of filtering data and making these csv files
GIPY05 = pd.read_csv("./data/GIPY05_filtered.csv")
GIPY04 = pd.read_csv("./data/GIPY04_filtered.csv")
GA03 = pd.read_csv("./data/GA03_filtered.csv")
GP02 = pd.read_csv("./data/GP02_filtered.csv")
GIPY0405 = pd.concat([GIPY04, GIPY05], ignore_index=True) #merging the csv files for GIPY04 and GIPY05

#global variables to keep track of the hovered and clicked stations for plotting
hov_station = station.Station('hover', None, None, None, 'blue')
click_stations = []

colours = ['darkred', 'limegreen', 'red', 'sienna', 'darkorange', 'darkgreen', 'darkviolet', 'deeppink']

###SUBPLOTS PLOTTING
def contains_colour(list_stations, colour):
    for s in list_stations:
        if s.colour == colour:
            return True
    return False

def get_colour():
    for c in colours:
        if contains_colour(click_stations, c) == False:
            return c
    return 'black'

#get lat and lons from hoverData
def set_hov_lat_lon_values(hov_data):
    global hov_station
    global click_stations
    # hovering over the clicked point doesn't give 'hovertext', so when there is no hovertext, set the hover data to the current click data
    if 'hovertext' in hov_data['points'][0]:
        hov_station.lat = hov_data['points'][0]['lat']
        hov_station.lon = hov_data['points'][0]['lon']
        hov_station.name = str(hov_data['points'][0]['hovertext'])
    elif len(click_stations) != 0:
        hov_station.lat, hov_station.lon, hov_station.name = None, None, None

#get lat and lons from clickData
def set_click_lat_lon_values(click_data, cruise, new_cruise):
    global click_stations
    #when the plot is initialized (click_data is None) or when the cruise has just changed (new_cruise == True), then we choose an initial click point
    if (click_data is None) or (new_cruise == True):
        pass
    # when you click on a point that is already clicked, the hovertext is not in the click_data dict
    # in that case, we keep the click_lat, lon and station the same
    elif 'hovertext' not in click_data['points'][0]:
        lat = click_data['points'][0]['lat']
        lon = click_data['points'][0]['lon']

        station.remove_from_list(lat, lon, click_stations)
    else:
        lat = click_data['points'][0]['lat']
        lon = click_data['points'][0]['lon']
        name = click_data['points'][0]['hovertext']
        click_stations.append(station.Station('click', lat, lon, name, get_colour()))


def get_x_y_values(cruise, lat, lon, data_name):
    #getting the x and y values to plot the depth profile for a given parameter (data_name) at a given lat and lon
    if cruise == 'GIPY0405':
        xvals = GIPY0405[data_name][(GIPY0405['Latitude'] == lat) & (GIPY0405['Longitude'] == lon)]
        yvals = GIPY0405['Depth'][(GIPY0405['Latitude'] == lat ) & (GIPY0405['Longitude'] == lon)]
    elif cruise == 'GA03':
        xvals = GA03[data_name][(GA03['Latitude'] == lat) & (GA03['Longitude'] == lon)]
        yvals = GA03['Depth'][(GA03['Latitude'] == lat) & (GA03['Longitude'] == lon)]
    elif cruise == 'GP02':
        xvals = GP02[data_name][(GP02['Latitude'] == lat) & (GP02['Longitude'] == lon)]
        yvals = GP02['Depth'][(GP02['Latitude'] == lat) & (GP02['Longitude'] == lon)]
    return [xvals, yvals]

def update_x_range(fig, x_range, cruise):
    #updating the x-axis range for the subplots
    if x_range == 'default':
        fig.update_xaxes(autorange=False)
        #adjusting the x-axis for temperature, ratio, density based on the cruise
        if cruise == 'GIPY0405':
            fig.update_xaxes(range=[-5, 25], row=1, col=1) #temp
            fig.update_xaxes(range=[-10, 650], row=1, col=6) #ratio
            fig.update_xaxes(range=[24, 28], row=1, col=2)  # density
        elif cruise == 'GA03':
            fig.update_xaxes(range=[5, 35], row=1, col=1) #temp
            fig.update_xaxes(range=[-10, 50], row=1, col=6) #ratio
            fig.update_xaxes(range=[22, 28], row=1, col=2)  # density
        elif cruise == 'GP02':
            fig.update_xaxes(range=[0, 30], row=1, col=1) #temp
            fig.update_xaxes(range=[-10, 250], row=1, col=6) #ratio
            fig.update_xaxes(range=[21, 28], row=1, col=2)  # density
        fig.update_xaxes(range=[30, 37], row=1, col=3) #salinity
        fig.update_xaxes(range=[-2, 45], row=1, col=4) #nitrate
        fig.update_xaxes(range=[-0.1, 2], row=1, col=5) #iron
    elif x_range == 'fitted':
        fig.update_xaxes(autorange=True) #letting plotly select the x-range for 'fitted' data
    fig.update_xaxes(nticks=3) #limiting the number of x-axis ticks so the plots don't change height
    return fig

def update_legend(fig, data_type, cruise):
    global hov_station, click_stations
    if data_type == 'hover':
        if hov_station.name is not None:
            fig['data'][0]['showlegend'] = True
            fig['data'][0]['name'] = str(hov_station.name) + '<br>lat: ' + str("{:.2f}".format(hov_station.lat)) \
                                     + '<br>lon: ' + str("{:.2f}".format(hov_station.lon))
    elif data_type == 'click':
        if (len(click_stations) != 0):
            for i in range(len(click_stations)):
                fig['data'][6 + 6 * i]['showlegend'] = True
                for i in range(len(click_stations)):
                    fig['data'][6 + 6 * i]['name'] = str(click_stations[i].name) + '<br>lat: ' + str("{:.2f}".format(click_stations[i].lat)) \
                                             + '<br>lon: ' + str("{:.2f}".format(click_stations[i].lon))
    if cruise == 'GIPY0405':
        fig.update_layout(legend_title_text='<b>' + 'GIPY04 & GIPY05' + '</b>' + '<br></br>Selected Stations:')
    else:
        fig.update_layout(legend_title_text='<b>' + str(cruise) + '</b>' + '<br></br>Selected Stations:')
    return fig

def clear_hover_traces(fig):
    global hov_station
    hov_station.lat, hov_station.lon, hov_station.name = None, None, None  # reset hover data for new cruise
    fig.data[0].update(x=[], y=[])
    fig.data[1].update(x=[], y=[])
    fig.data[2].update(x=[], y=[])
    fig.data[3].update(x=[], y=[])
    fig.data[4].update(x=[], y=[])
    fig.data[5].update(x=[], y=[])
    return fig

def clear_click_traces(fig):
    global click_stations
    click_stations = []
    for i in range(8):
        fig.data[6 + i * 6].update(x=[], y=[])
        fig.data[7 + i * 6].update(x=[], y=[])
        fig.data[8 + i * 6].update(x=[], y=[])
        fig.data[9 + i * 6].update(x=[], y=[])
        fig.data[10 + i * 6].update(x=[], y=[])
        fig.data[11 + i * 6].update(x=[], y=[])
    return fig

#initialize the profiles
def initialize_profiles(cruise, x_range, y_range):
    #global click_stations
    fig = make_subplots(rows=1, cols=6, subplot_titles=("<b>Temperature</b>", "<b>Sigma0*</b>", "<b>Salinity</b>", "<b>Nitrate</b>",
                                                        "<b>Iron</b>", "<b>Nitrate/Iron</b>"))


    # empty traces for hovered data
    figT = px.scatter(x=[None], y=[None], color_discrete_sequence=['blue'])
    figS = px.scatter(x=[None], y=[None], color_discrete_sequence=['blue'])
    figN = px.scatter(x=[None], y=[None], color_discrete_sequence=['blue'])
    figI = px.scatter(x=[None], y=[None], color_discrete_sequence=['blue'])
    figR = px.scatter(x=[None], y=[None], color_discrete_sequence=['blue'])
    figD = px.scatter(x=[None], y=[None], color_discrete_sequence=['blue'])

    #print(figT.data[0])
    fig.add_trace(figT.data[0], row=1, col=1)
    fig.add_trace(figD.data[0], row=1, col=2)
    fig.add_trace(figS.data[0], row=1, col=3)
    fig.add_trace(figN.data[0], row=1, col=4)
    fig.add_trace(figI.data[0], row=1, col=5)
    fig.add_trace(figR.data[0], row=1, col=6)


    for i in range(8):
        #traces for clicked data
        figT = px.scatter(x=[None], y=[None])
        figD = px.scatter(x=[None], y=[None])
        figS = px.scatter(x=[None], y=[None])
        figN = px.scatter(x=[None], y=[None])
        figI = px.scatter(x=[None], y=[None])
        figR = px.scatter(x=[None], y=[None])


        fig.add_trace(figT.data[0], row=1, col=1)
        fig.add_trace(figD.data[0], row=1, col=2)
        fig.add_trace(figS.data[0], row=1, col=3)
        fig.add_trace(figN.data[0], row=1, col=4)
        fig.add_trace(figI.data[0], row=1, col=5)
        fig.add_trace(figR.data[0], row=1, col=6)


    #fig = update_legend(fig, None, cruise)
    fig.update_yaxes(range=y_range)
    #putting x-axis on top of the plot
    fig.update_layout(xaxis=dict(side='top'), xaxis2=dict(side='top'), xaxis3=dict(side='top'), xaxis4=dict(side='top'), xaxis5=dict(side='top'), xaxis6=dict(side='top'))
    fig.update_annotations(yshift=-410) #moving titles to bottom of plot
    fig.update_layout(margin={'l': 0, 'b': 40, 'r': 100, 't': 30})

    #customize x axes
    fig.update_xaxes(title_text='deg C', row=1, col=1)
    fig.update_xaxes(title_text="kg/m\u00B3", row=1, col=2) #unicode for the m^3
    fig.update_xaxes(title_text='Practical Salinity', row=1, col=3)
    fig.update_xaxes(title_text="umol/kg", row=1, col=4)
    fig.update_xaxes(title_text="nmol/kg", row=1, col=5)
    fig.update_xaxes(title_text="umol/nmol", row=1, col=6)


    fig = update_x_range(fig, x_range, cruise)
    fig = update_legend(fig, 'click', cruise)

    return fig

def switch_profiles(click_data, cruise, fig, x_range, y_range):
    #global click_stations
    #set_click_lat_lon_values(click_data, cruise, True)

    fig = clear_hover_traces(fig)
    fig = clear_click_traces(fig)

    #update ylim
    fig.update_yaxes(range=y_range)

    #update xlims for temp based on cruise
    fig = update_x_range(fig, x_range, cruise)

    #display cruise info
    fig = update_legend(fig, 'click', cruise)

    return fig

def update_profiles(hov_data, click_data, cruise, fig, x_range, y_range):
    global click_stations, hov_station

    if hov_data != None:
        #set_hov_lat_lon_values(hov_data)

        hov_xvals_temp, hov_yvals_temp = get_x_y_values(cruise, hov_station.lat, hov_station.lon, 'Temperature')
        hov_xvals_dens, hov_yvals_dens = get_x_y_values(cruise, hov_station.lat, hov_station.lon, 'Density')
        hov_xvals_sal, hov_yvals_sal = get_x_y_values(cruise, hov_station.lat, hov_station.lon, 'Salinity')
        hov_xvals_nit, hov_yvals_nit = get_x_y_values(cruise, hov_station.lat, hov_station.lon, 'Nitrate')
        hov_xvals_iron, hov_yvals_iron = get_x_y_values(cruise, hov_station.lat, hov_station.lon, 'Iron')
        hov_xvals_ratio, hov_yvals_ratio = get_x_y_values(cruise, hov_station.lat, hov_station.lon, 'Ratio')


        fig.data[0].update(x=hov_xvals_temp, y=hov_yvals_temp)
        fig.data[1].update(x=hov_xvals_dens, y=hov_yvals_dens)
        fig.data[2].update(x=hov_xvals_sal, y=hov_yvals_sal)
        fig.data[3].update(x=hov_xvals_nit, y=hov_yvals_nit)
        fig.data[4].update(x=hov_xvals_iron, y=hov_yvals_iron)
        fig.data[5].update(x=hov_xvals_ratio, y=hov_yvals_ratio)

    else:
        fig = clear_hover_traces(fig)

    if click_data is not None:
        #set_click_lat_lon_values(click_data, cruise, False)

        for i in range(8):
            if i < len(click_stations):
                click_xvals_temp, click_yvals_temp = get_x_y_values(cruise, click_stations[i].lat, click_stations[i].lon, 'Temperature')
                click_xvals_dens, click_yvals_dens = get_x_y_values(cruise, click_stations[i].lat, click_stations[i].lon, 'Density')
                click_xvals_sal, click_yvals_sal = get_x_y_values(cruise, click_stations[i].lat, click_stations[i].lon, 'Salinity')
                click_xvals_nit, click_yvals_nit = get_x_y_values(cruise, click_stations[i].lat, click_stations[i].lon, 'Nitrate')
                click_xvals_iron, click_yvals_iron = get_x_y_values(cruise, click_stations[i].lat, click_stations[i].lon, 'Iron')
                click_xvals_ratio, click_yvals_ratio = get_x_y_values(cruise, click_stations[i].lat, click_stations[i].lon, 'Ratio')


                fig.data[6 + i * 6].update(x=click_xvals_temp, y=click_yvals_temp, marker_color=click_stations[i].colour)
                fig.data[7 + i * 6].update(x=click_xvals_dens, y=click_yvals_dens, marker_color=click_stations[i].colour)
                fig.data[8 + i * 6].update(x=click_xvals_sal, y=click_yvals_sal, marker_color=click_stations[i].colour)
                fig.data[9 + i * 6].update(x=click_xvals_nit, y=click_yvals_nit, marker_color=click_stations[i].colour)
                fig.data[10 + i * 6].update(x=click_xvals_iron, y=click_yvals_iron, marker_color=click_stations[i].colour)
                fig.data[11 + i * 6].update(x=click_xvals_ratio, y=click_yvals_ratio, marker_color=click_stations[i].colour)

            else:
                fig.data[6 + i * 6].update(x=[], y=[])
                fig.data[7 + i * 6].update(x=[], y=[])
                fig.data[8 + i * 6].update(x=[], y=[])
                fig.data[9 + i * 6].update(x=[], y=[])
                fig.data[10 + i * 6].update(x=[], y=[])
                fig.data[11 + i * 6].update(x=[], y=[])


    #display cruise info
    fig = update_legend(fig, 'click', cruise)
    fig = update_legend(fig, 'hover', cruise)

    #update xlim
    fig = update_x_range(fig, x_range, cruise)
    #update ylim
    fig.update_yaxes(range=y_range)

    return fig




###MAP PLOTTING

#initializes click marker for map
def map_initialize_cruise(fig, cruise):
    global click_stations
    set_click_lat_lon_values(None, cruise, False)
    for i in range(len(click_stations)):
        fig.add_trace(go.Scattermapbox(lat=[click_stations[i].lat], lon=[click_stations[i].lon], showlegend=False, hovertemplate="<b>" + str(click_stations[i].name) +
                                         "</b><br><br>Latitude=%{lat} </br> Longitude=%{lon}<extra></extra>",
                                       mode='markers', marker=go.scattermapbox.Marker(size=10, color=click_stations[i].colour)))
        #fig.update(lataxis_showgrid=True, lonaxis_showgrid=True)
        #fig.update_geos(lataxis_showgrid=True, lonaxis_showgrid=True)



    return fig

def plot_stations(cruise):
    if cruise == 'GIPY0405':
        fig = px.scatter_mapbox(GIPY0405, lat="Latitude", lon="Longitude", hover_name="Station",
                                color_discrete_sequence=['blue'], zoom=1.2, center=dict(lat=-50, lon=0))
    elif cruise == 'GA03':
        fig = px.scatter_mapbox(GA03, lat="Latitude", lon="Longitude", hover_name="Station",
                                color_discrete_sequence=['blue'],
                                zoom=1.2)
    elif cruise == 'GP02':
        fig = px.scatter_mapbox(GP02, lat="Latitude", lon="Longitude", hover_name="Station",
                                color_discrete_sequence=['blue'],
                                zoom=1.2)
    fig.update_layout(mapbox_style="open-street-map")


    # adding markers from: https://plotly.com/python/scattermapbox/
    if (len(click_stations) != 0):
        for i in range(len(click_stations)):
            fig.add_trace(go.Scattermapbox(lat=[click_stations[i].lat], lon=[click_stations[i].lon], showlegend=False,
                                           hovertemplate="<b>" + str(click_stations[i].name) +
                                                         "</b><br><br>Latitude=%{lat} </br> Longitude=%{lon}<extra></extra>",
                                           mode='markers', marker=go.scattermapbox.Marker(size=10, color=click_stations[i].colour)))

    return fig

#figure functions
def initialize_map(cruise):

    fig = plot_stations(cruise)

    fig = map_initialize_cruise(fig, cruise)  # initializes the click for the new cruise

    if cruise == 'GIPY0405':
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title='GIPY04 and GIPY05')
    else:
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title=cruise)

    return fig

# update map for cruise changes
def switch_map(cruise, fig):
    fig.data = []
    fig = plot_stations(cruise)
    
    fig = map_initialize_cruise(fig, cruise)  # initializes the click for the new cruise

    if cruise == 'GIPY0405':
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title='GIPY04 and GIPY05')
    else:
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title=cruise)

    return fig


def update_map(hov_data, click_data, figure_data, cruise, fig):
    global hov_station, click_stations
    if hov_data != None:
        set_hov_lat_lon_values(hov_data)
    set_click_lat_lon_values(click_data, cruise, False)

    #set_click_lat_lon_values(click_data, cruise, False)
    # Dot color, map type and map zoom are interactive.
    # code from https://plotly.com/python/mapbox-layers/ without the "fig.show".
    fig = plot_stations(cruise)
    if figure_data is not None: #set map layout to its previous settings, so the zoom and position doesn't reset
        fig.layout['mapbox'] = figure_data['layout']['mapbox']


    if cruise == 'GIPY0405':
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title='GIPY04 and GIPY05')
    else:
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title=cruise)
    return fig