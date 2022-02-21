import dash  # pip install dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input

from dash_extensions import Lottie  # pip install dash-extensions
import dash_bootstrap_components as dbc  # pip install dash-bootstrap-components
import plotly.express as px  # pip install plotly
import plotly.graph_objs as go
import pandas as pd  # pip install pandas
from datetime import date
import calendar
from wordcloud import WordCloud  # pip install wordcloud

from dash_bootstrap_templates import load_figure_template

load_figure_template("cyborg")

# Lottie by Emil - https://github.com/thedirtyfew/dash-extensions
url_globe = "https://assets5.lottiefiles.com/packages/lf20_hzwndued.json"
url_globe_death = "https://assets1.lottiefiles.com/packages/lf20_3rwBPO.json"
url_globe_active = "https://assets9.lottiefiles.com/packages/lf20_dcU5CK.json"
url_globe_vaccine = "https://assets2.lottiefiles.com/packages/lf20_zv39zodk.json"
url_reactions = "https://assets2.lottiefiles.com/packages/lf20_nKwET0.json"
options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))

url_vaccinces = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'
vaccine_data = pd.read_csv(url_vaccinces)
# Fix the date for vaccination data
vaccine_data['date'] = pd.to_datetime(vaccine_data['date'])
vaccine_data['daily_vaccinations'] = vaccine_data['daily_vaccinations'].fillna(0)
vaccine_data['people_fully_vaccinated'] = vaccine_data['people_fully_vaccinated'].fillna(0)

vaccine_data_1 = vaccine_data.groupby(['date','location'])[['daily_vaccinations', 'people_fully_vaccinated',
                                                'people_vaccinated','total_vaccinations']].sum().reset_index()

vaccinations = vaccine_data_1.groupby(['date', 'location'])['people_fully_vaccinated',
                                                            'people_vaccinated'].sum().reset_index()

fully_vaccinated = vaccinations[vaccinations['location'] == 'World']['people_fully_vaccinated'].iloc[-1]

url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

confirmed = pd.read_csv(url_confirmed)
deaths = pd.read_csv(url_deaths)
recovered = pd.read_csv(url_recovered)

# Unpivot data frames
date1 = confirmed.columns[4:]
total_confirmed = confirmed.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=date1,
                                 var_name='date', value_name='confirmed')
date2 = deaths.columns[4:]
total_deaths = deaths.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=date2,
                           var_name='date', value_name='death')
date3 = recovered.columns[4:]
total_recovered = recovered.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=date3,
                                 var_name='date', value_name='recovered')

# Merging data frames
covid_data = total_confirmed.merge(right=total_deaths, how='left',
                                   on=['Province/State', 'Country/Region', 'date', 'Lat', 'Long'])
covid_data = covid_data.merge(right=total_recovered, how='left',
                              on=['Province/State', 'Country/Region', 'date', 'Lat', 'Long'])

# Converting date column from string to proper date format
covid_data['date'] = pd.to_datetime(covid_data['date'])

# Check how many missing values naN
covid_data.isna().sum()

# Replace naN with 0
covid_data['recovered'] = covid_data['recovered'].fillna(0)

# Create new column
covid_data['active'] = covid_data['confirmed'] - covid_data['death'] - covid_data['recovered']

covid_data_1 = covid_data.groupby(['date'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()

# Create dictionary of list
covid_data_list = covid_data[['Country/Region', 'Lat', 'Long']]
dict_of_locations = covid_data_list.set_index('Country/Region')[['Lat', 'Long']].T.to_dict('dict')

# Bootstrap themes by Ann: https://hellodash.pythonanywhere.com/theme_explorer
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src='/assets/corona.jpeg')
            ], className='mb-2 ')

        ], width=3),
        dbc.Col([

        ], width=2),
        dbc.Col([
            dbc.Card([
                html.H3('Covid-19 Dashboard'),
                html.H5('Global Overview')
            ], style={'textAlign': 'center', 'color': 'white', 'margin-top': '100px'}, )

        ], width=4),
        dbc.Col([
            html.H6('Last Updated: ' + str(covid_data['date'].iloc[-1].strftime('%B %d, %Y')) + ' 00:01 (UTC)',
                    style={'color': 'orange'})
        ])

    ], className='mb-2 mt-3'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="25%", height="25%", url=url_globe),
                               style={'background-color': '#1A1100'}),
                dbc.CardBody([
                    html.H6('Global Cases',
                            style={'textAlign': 'center',
                                   'color': 'white'}),
                    html.P(f"{covid_data_1['confirmed'].iloc[-1]:,.0f}",
                           style={'textAlign': 'center',
                                  'color': 'orange',
                                  'fontSize': 40}),
                    html.P('new: ' + f"{covid_data_1['confirmed'].iloc[-1] - covid_data_1['confirmed'].iloc[-2]:,.0f}"
                           + ' (' + str(
                        round(((covid_data_1['confirmed'].iloc[-1] - covid_data_1['confirmed'].iloc[-2]) /
                               covid_data_1['confirmed'].iloc[-1]) * 100, 2)) + '%)',
                           style={'textAlign': 'center',
                                  'color': 'orange',
                                  'fontSize': 15,
                                  'margin-top': '-18px'})
                ])
            ], color='#1f2c56', style={'width': '18', 'box-shadow': '2px 2px 2px #1f2c56'}, outline=True)
        ], width=3),

        dbc.Col([

        ], width=0.5),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="23%", height="23%", url=url_globe_death),
                               style={'background-color': '#1A1100'}),
                dbc.CardBody([
                    html.H6(children='Global Deaths',
                            style={'textAlign': 'center',
                                   'color': 'white'}),
                    html.P(f"{covid_data_1['death'].iloc[-1]:,.0f}",
                           style={'textAlign': 'center',
                                  'color': '#dd1e35',
                                  'fontSize': 40}),
                    html.P('new: ' + f"{covid_data_1['death'].iloc[-1] - covid_data_1['death'].iloc[-2]:,.0f}"
                           + ' (' + str(round(((covid_data_1['death'].iloc[-1] - covid_data_1['death'].iloc[-2]) /
                                               covid_data_1['death'].iloc[-1]) * 100, 2)) + '%)',
                           style={'textAlign': 'center',
                                  'color': '#dd1e35',
                                  'fontSize': 15,
                                  'margin-top': '-18px'})
                ])
            ], color='#1f2c56', style={'width': '18', 'box-shadow': '2px 2px 2px #1f2c56'}, outline=True)

        ], width=3),

        dbc.Col([

        ], width=0.5),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="40%", height="40%", url=url_globe_active),
                               style={'background-color': '#1A1100'}),
                dbc.CardBody([
                    html.H6(children='Global Active',
                            style={'textAlign': 'center',
                                   'color': 'white'}),
                    html.P(f"{covid_data_1['active'].iloc[-1]:,.0f}",
                           style={'textAlign': 'center',
                                  'color': '#e55467',
                                  'fontSize': 40}),
                    html.P('new: ' + f"{covid_data_1['active'].iloc[-1] - covid_data_1['active'].iloc[-2]:,.0f}"
                           + ' (' + str(round(((covid_data_1['active'].iloc[-1] - covid_data_1['active'].iloc[-2]) /
                                               covid_data_1['active'].iloc[-1]) * 100, 2)) + '%)',
                           style={'textAlign': 'center',
                                  'color': '#e55467',
                                  'fontSize': 15,
                                  'margin-top': '-18px'})
                ])
            ], color='#1f2c56', style={'width': '18', 'box-shadow': '2px 2px 2px #1f2c56'}, outline=True)

        ], width=3),

        dbc.Col([

        ], width=0.5),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="23%", height="23%", url=url_globe_vaccine),
                               style={'background-color': '#1A1100'}),
                dbc.CardBody([
                    html.H6(children='People Fully Vaccinated',
                            style={'textAlign': 'center',
                                   'color': 'white'}),
                    html.P(f"{fully_vaccinated:,.0f}",
                           style={'textAlign': 'center',
                                  'color': 'green',
                                  'fontSize': 40}),
                    html.P(
                        'new: ' + f"{vaccinations[vaccinations['location'] == 'World']['people_fully_vaccinated'].iloc[-1] - vaccinations[vaccinations['location'] == 'World']['people_fully_vaccinated'].iloc[-2]:,.0f}"
                        + ' (' + str(round(
                            ((vaccinations[vaccinations['location'] == 'World']['people_fully_vaccinated'].iloc[-1] - vaccinations[vaccinations['location'] == 'World']['people_fully_vaccinated'].iloc[-2]) / vaccinations[vaccinations['location'] == 'World']['people_fully_vaccinated'].iloc[-1]) * 100,2)) + '%)',

                        style={'textAlign': 'center',
                               'color': 'green',
                               'fontSize': 15,
                               'margin-top': '-18px'})
                ])
            ], color='#1f2c56', style={'width': '18', 'box-shadow': '2px 2px 2px #1f2c56'}, outline=True)

        ], width=3),

    ], className='mb-2 mt-5'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4('Select Country:', style={'color': 'white'}),
                    dcc.Dropdown(id='w_countries',
                                 multi=False,
                                 searchable=True,
                                 value='US',
                                 placeholder='Select Countries',
                                 options=[{'label': c, 'value': c}
                                          for c in (covid_data['Country/Region'].unique())],style={'color':'black'})
                ])
            ], color='#1f2c56', style={'width': '18', 'box-shadow': '2px 2px 2px 2px #1f2c56'}, outline=True),
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='confirmed')

                ])
            ], color='#1f2c56', style={'width': '18', 'box-shadow': '2px 2px 2px #1f2c56'}, outline=True),
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='death')

                ])
            ], color='#1f2c56', style={'width': '18', 'box-shadow': '2px 2px 2px #1f2c56'}, outline=True),
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='recovered')

                ])
            ], color='#1f2c56', style={'width': '18', 'box-shadow': '2px 2px 2px #1f2c56'}, outline=True),
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='active')

                ])
            ], color='#1f2c56', style={'width': '18', 'box-shadow': '2px 2px 2px #1f2c56'}, outline=True)
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5('Case Breakdown', style={'color': 'white', 'text-align': 'center'})

                ]),
                dbc.CardBody([
                    dcc.Graph(id='pie_chart'),
                ])

            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5('Daily Cases', style={'color': 'white', 'text-align': 'center'})

                ]),
                dbc.CardBody([
                    dcc.Graph(id='line_chart'),
                ])

            ]),

        ], width=6, className='h-100'),

    ], className='mb-1 mt-5')

], fluid=True)


@app.callback(
    Output('pie_chart', 'figure'),
    [Input('w_countries', 'value')]
)
def update_pie_chart(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[
        ['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    confirmed_value = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-1]
    death_value = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-1]
    recovered_value = covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-1]
    active_value = covid_data_2[covid_data_2['Country/Region'] == w_countries]['active'].iloc[-1]
    color = ['orange', 'green', '#e55467', '#dd1e35']
    labels = ['Confirmed', 'Death', 'Recovered', 'Active']
    values = [confirmed_value, death_value, recovered_value, active_value]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0, 0.7, 0] )])
    fig.update_traces(hoverinfo='label+percent', textinfo='label+value', textfont_size=15,
                      title={'text': 'Total Cases: ' + (w_countries),
                             },
                      titlefont={'color': 'white',
                                 'size': 20},
                      

                      ),

    return fig


@app.callback(Output('line_chart', 'figure'),
              [Input('w_countries', 'value')])
def update_line_chart(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[
        ['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    covid_data_3 = covid_data_2[covid_data_2['Country/Region'] == w_countries][
        ['Country/Region', 'date', 'confirmed']].reset_index()
    covid_data_3['daily confirmed'] = covid_data_3['confirmed'] - covid_data_3['confirmed'].shift(1)
    covid_data_3['Rolling Ave.'] = covid_data_3['daily confirmed'].rolling(window=7).mean()

    fig = go.Figure()

    fig.add_trace(go.Bar(x=covid_data_3['date'].tail(30),
                         y=covid_data_3['daily confirmed'].tail(30),
                         name='Daily Confirmed Cases',
                         # marker_color='#1ec9ac'
                         )
                  ),
    fig.update_layout(
        title={
            'text': "Last 30 Days Confirmed Cases: " + (w_countries),
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        legend={'orientation': 'h',
                'bgcolor': '#1f2c56',
                'xanchor': 'center', 'x': 0.5, 'y': -0.7},

    )

    fig.add_trace(go.Scatter(
        x=covid_data_3['date'].tail(30),
        y=covid_data_3['Rolling Ave.'].tail(30),
        mode='lines',
        name='Rolling Average of the last 7 days - daily confirmed cases'

    ))

    return fig


@app.callback(Output('confirmed', 'figure'),
              [Input('w_countries', 'value')])
def update_confirmed(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[
        ['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    value_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-1] - \
                      covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-2]
    delta_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-2] - \
                      covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-3]

    return {
        'data': [go.Indicator(
            mode='number+delta',
            value=value_confirmed,
            delta={'reference': delta_confirmed,
                   'position': 'right',
                   'valueformat': ',g',
                   'relative': False,
                   'font': {'size': 15}},
            number={'valueformat': ',',
                    'font': {'size': 20}},
            domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'New Confirmed',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=50,

        )
    }


@app.callback(Output('death', 'figure'),
              [Input('w_countries', 'value')])
def update_confirmed(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[
        ['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    value_death = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-1] - \
                  covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-2]
    delta_death = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-2] - \
                  covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-3]

    return {
        'data': [go.Indicator(
            mode='number+delta',
            value=value_death,
            delta={'reference': delta_death,
                   'position': 'right',
                   'valueformat': ',g',
                   'relative': False,
                   'font': {'size': 15}},
            number={'valueformat': ',',
                    'font': {'size': 20}},
            domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'New Death',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='#dd1e35'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=50,

        )
    }


@app.callback(Output('recovered', 'figure'),
              [Input('w_countries', 'value')])
def update_confirmed(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[
        ['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    value_recovered = covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-1] - \
                      covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-2]
    delta_recovered = covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-2] - \
                      covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-3]

    return {
        'data': [go.Indicator(
            mode='number+delta',
            value=value_recovered,
            delta={'reference': delta_recovered,
                   'position': 'right',
                   'valueformat': ',g',
                   'relative': False,
                   'font': {'size': 15}},
            number={'valueformat': ',',
                    'font': {'size': 20}},
            domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'New Recovered',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='green'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=50,

        )
    }


@app.callback(Output('active', 'figure'),
              [Input('w_countries', 'value')])
def update_confirmed(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[
        ['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    value_active = covid_data_2[covid_data_2['Country/Region'] == w_countries]['active'].iloc[-1] - \
                   covid_data_2[covid_data_2['Country/Region'] == w_countries]['active'].iloc[-2]
    delta_active = covid_data_2[covid_data_2['Country/Region'] == w_countries]['active'].iloc[-2] - \
                   covid_data_2[covid_data_2['Country/Region'] == w_countries]['active'].iloc[-3]

    return {
        'data': [go.Indicator(
            mode='number+delta',
            value=value_active,
            delta={'reference': delta_active,
                   'position': 'right',
                   'valueformat': ',g',
                   'relative': False,
                   'font': {'size': 15}},
            number={'valueformat': ',',
                    'font': {'size': 20}},
            domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'New Active',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='#e55467'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=50,

        )
    }


if __name__ == "__main__":
    app.run_server(debug=False, host= '127.0.0.1', port=8006)
