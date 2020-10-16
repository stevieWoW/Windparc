import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import *
import dash_daq as daq
import configparser
import numpy as np
import datetime
import logging
import dash_function
import pandas as pd
import plotly.express as px

##################################################
#initialize the log file
logging.basicConfig(format = '%(asctime)s ' + "[%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s", filename='/var/log/dash/dash.log', level = logging.DEBUG)


##################################################
#Declare Variables

#get WindmillNames
dfwindmillname=dash_function.dash_function.ExecuteQuery(
        [
            {
                "rows":"WM.WINDMILL",
                "table":"Metabase.WIND_MILL WM",
                "where":[{"Operator":"","WM.LOCATION":"<>1"}],
            }
        ],"WindmillName",False
    )

monthname=["Januar","February","March","April","May","June","July","August","September","October","November","December"]

app = dash.Dash(__name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])


##################################################
# some design patterns
design = {
    'colors' : {
        'background': 'rgb(30,30,30)',
        'text': 'rgb(127, 219, 255)',
        'BarPlan':'rgb(54,81,215)',
		'BarIs':'rgb(107,124,209)',
        'BarInvest':'rgb(0,128,255)',
        'BarIncome':'rgb(255,255,102)',
        'BarTax':'rgb(255,153,153)',
        'BarWin':'rgb(0,153,0)',
        'BarLose':'rgb(153,0,0)',
        'PieType':['gold', 'mediumturquoise', 'darkorange']
    },

    'body' : {
        'backgroundColor': 'rgb(17,17,17)',
        'margin': '0px',
        'height': '1000px',
        'position' : 'relative'
    }
    
}

##################################################
#include the map
location = pd.read_csv("/var/www/html/Dash/assets/WindparcLocation.csv")
figlocation = px.scatter_mapbox(location, lat="lat", lon="lon", hover_name="City", hover_data=["Location", "Number"],
                        color_discrete_sequence=["fuchsia"], zoom=11, height=500,color="Number", size="Number",
                        color_continuous_scale=px.colors.diverging.BrBG,size_max=20)
figlocation.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "openstreetmap.org",
            "source": [
                "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png"
            ]
        }
      ])

figlocation.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


##################################################
app.layout = html.Div(style=design['body'],children=[
##################################################
# Header
    html.Div(id='header', children=[
        html.Div(id='logo',children=[
            html.Img(src='assets/windmill.png',className='windmill-1')
        ]),
        html.H1(
            children='WindParc - Dashboard - Development',
            style={
                'textAlign': 'center',
                'color': 'rgb(255,255,255)'
            }
        ),
        html.Div(children=' Lorup ', style={
            'textAlign': 'center',
            'color': 'rgb(180,180,180)'
        }),
    ]),
    
    
    html.Hr(),

# Header end
##################################################
##################################################
# sidemenu
    html.Div(id='sidemenu',className='sidenav',children=[
        html.H2('Settings',style={'color':'rgb(161, 159, 153)','margin':'2%'}),
        
        html.Hr(style={'border-color':'rgb(17,17,17)'}),
        html.H6('Aggregation',style={'color':'rgb(161, 159, 153)','margin':'2%'}),
        dcc.RadioItems(
            id='aggregation',
            options=[
                {'label': 'year', 'value': 'YEAR'},
                {'label': 'month', 'value': 'MONTH'},
                {'label': 'windmill', 'value': 'WINDMILL'}
            ],
            value='MONTH',
            labelStyle={'display': 'inline-block'}
        ) ,
        html.Hr(style={'border-color':'rgb(40,40,40)','margin-left':'30px','margin-right':'30px'}),
        dcc.Dropdown(id='location',options=dash_function.dash_function.GetLabel("select WL.LOCATION, WL.ID from Metabase.WIND_LOCATION WL;"),
        value='1',
        style={
            'width':'260px',
            'backgroundColor':'black',
            'color':'white',
            'margin':'2%'
            },
        clearable=False
        ),
##################################################
##################################################
# slideryear        
        html.Div(id='slideryear', className="col-10", children=[
            dcc.Checklist(
                id='checkboxyear',
                options=[
                    {'label': 'year', 'value': 'true'},
                ],
                value = ['true']
            ),
            dcc.RangeSlider(
            id='rangeslideryear',
            className='col-8',
            allowCross=False,
            value=[int( datetime.datetime.now().year) - 1 ,int(datetime.datetime.now().year)],
            step=1,
            min=2017,
            marks={i + 1: '{}'.format(i + 1) for i in range(2016,int(datetime.datetime.now().year),1)},
            max=int(datetime.datetime.now().year),
            #persistence=True,
            #persistence_type='session',
            updatemode='mouseup',
        )
        ]),
##################################################
##################################################
# slidermonth
        html.Div(id='slidermonth', className="col-10", children=[
            dcc.Checklist(
                id='checkboxmonth',
                options=[
                    {'label': 'month', 'value': 'true'},
                ],
            ),
            dcc.RangeSlider(
            id='rangeslidermonth',
            className='col-8',
            allowCross=False,
            value=[3,5],
            step=1,
            min=1,
            marks={i + 1: '{}'.format(i + 1) for i in range(12)},
            max=12,
            #persistence=True,
            #persistence_type='session',
            updatemode='mouseup',
        )
        ]),
##################################################
##################################################
# windmill
        html.Hr(style={'border-color':'rgb(40,40,40)','margin-left':'30px','margin-right':'30px'}),
        dcc.Dropdown(id='windmill',
        multi=True,
        #value=None,
        style={
            'width':'260px',
            'backgroundColor':'black',
            'color':'white',
            'margin':'2%',
            'float':'left'
            },
        clearable=False
        ),
        
        html.Button(id='button',style={'float':'left', 'display':'block','margin':'2%'},children='select')
    ]),
# Sidemenu end
##################################################
html.H1('Graphs',id='h1graph',style={'color':'rgb(161, 159, 153)'}),
html.Hr(id='graphhr',style={'border-color':'rgb(17,17,17)'}),
##################################################
# container for graphs
    html.Div(id='graphcontainer', children=[
##################################################
#graph one
    html.Div(className='placeholdergraph col-10 bradius-4',children=[
        dcc.Graph(id='Performancebar',figure={
            'layout' :{
                'paper_bgcolor': design['colors']['background'],
                'plot_bgcolor': design['colors']['background'],
            }
        })  
    ]),
# end graph one
##################################################
##################################################
# graph two
    html.Div(id='invest-div',className='placeholdergraph col-5 bradius-4',children=[
        dcc.Checklist(id='totalinvest',
    options=[
        {'label': 'total', 'value': 'total'}
    ],
    value=[],
    style={'position':'absolute','z-index':'9999'}
),
        dcc.Graph(
            id='Invest',
            figure={
                'layout': {
                    'plot_bgcolor': design['colors']['background'],
                    'paper_bgcolor': design['colors']['background'],
                    'font': {
                        'color': design['colors']['text']
                        }

                }
            }

        )
    ]),
# end graph two
##################################################
##################################################
# graph three
    html.Div(className='placeholdergraph col-5 bradius-4',children=[
        dcc.Graph(
            id='Windspeed',
            figure={
                'layout': {
                    'plot_bgcolor': design['colors']['background'],
                    'paper_bgcolor': design['colors']['background'],
                    'font': {
                        'color': design['colors']['text']
                        }
                }
            }

        )
    ]),
# end graph three
##################################################
##################################################
# graph four
    html.Div(className='placeholdergraph col-4 bradius-4',children=[
        daq.Gauge(
            id='Performancegauge',
            showCurrentValue=True,
            units="%",
            color={"gradient":True,"ranges":{"red":[0,60],"yellow":[60,80],"green":[80,100]}},
            label='Performance',
            max=100,
            min=0
        )
    ]),
# end graph four
##################################################
##################################################
# graph five
    html.Div(className='placeholdergraph col-6 bradius-4',id="Windmill",children=[
        dcc.Graph(
            id='WindmillNumber',
            figure={
                'layout': {
                    'plot_bgcolor': design['colors']['background'],
                    'paper_bgcolor': design['colors']['background'],
                    'font': {
                        'color': design['colors']['text']
                        }
                }
            }
        )
    ]),
# end graph five
##################################################
##################################################
# graph six
    html.Div(className='placeholdergraph col-10 bradius-4',children=[
        dcc.Graph(
            id='Location',
            figure=figlocation
        )
    ]),
# end graph five
    ])# Close GraphContainer
])# Close app.layout

##################################################
#start with callbacks

@app.callback(
    [Output('Performancebar','figure'),
     Output('WindmillNumber','figure'),
     Output('Performancegauge','value')],
    [Input('button','n_clicks')],
    [State('aggregation','value'),
     State('location','value'),
     State('checkboxyear','value'),
     State('checkboxmonth','value'),
     State('rangeslideryear','value'),
     State('rangeslidermonth','value'),
     State('windmill','value')]
)
def UpdatePerformance(n_clicks,aggregation,location,checkboxyear,checkboxmonth,rangeslideryear,rangeslidermonth,windmill):
    #Function to update the Performance Graph that shows PLAN/IS Values
    #These values depends on the input of the Settings on the left side
    #You can show the PLAN/IS of a single windmill, a parc or combined
    #this function also affects Performance Gauge and Windmill Pie Chart

    #log some information to track much easier
    logging.debug('Year: {},{}'.format(checkboxyear,rangeslideryear))
    logging.debug('Month: {},{}'.format(checkboxmonth,rangeslidermonth))
    logging.debug('Aggregation: {}'.format(aggregation))
    logging.debug('Location {}'.format(location))
    logging.debug('windmill: {}'.format(windmill))

    #define some Variables
    pielocation="2,3,4"
    mill=None

    #set hover header in PerformanceBarchart
    if aggregation == "MONTH":
        if checkboxmonth:
            header=monthname[rangeslidermonth[0] - 1:rangeslidermonth[1]]
        else:
            header=monthname
    elif aggregation == "WINDMILL":
        header=dfwindmillname['WINDMILL']
    else:
        h=[*range(rangeslideryear[0],rangeslideryear[1] + 1)]
        header=["YEAR"] * len(h)
        del h


    #get the where statement
    where = dash_function.dash_function.CheckBoxYearMonth("WEP",checkboxyear,checkboxmonth,rangeslideryear,rangeslidermonth,[".YEAR",".MONTH"]) 
    wheregauge = where # make a copy of where for performance

    #get the mills picked in the dropdown
    if windmill is None or len(windmill) == 0:
        if int(location) is not 1:
            mill = dash_function.dash_function.Windmill(location,None)
            where.append({"Operator":"AND","WEP.WINDMILL":" in(" + mill + ")"})
            pielocation=str(location)
    else:
        mill = dash_function.dash_function.Windmill(None,windmill)
        where.append({"Operator":"AND","WEP.WINDMILL":" in(" + mill + ")"})
    

    #get the dataframe of the collected windmill performance
    df = dash_function.dash_function.ExecuteQuery(
        [
            {
                "rows":"sum(WEP.PLANPERFORMANCE) as _PLAN, sum(WEP.ISPERFORMANCE) as _IS, WEP." + aggregation,
                "table":"Metabase.WIND_ENERGY_PERFORMANCE WEP",
                "where":where,
                "groupby":"WEP." + aggregation
            }
        ],"PlanIsPerformance",False
    )
    #print the where statement
    logging.debug("where: {0}".format(where))


    ########### some test #########################
    #check if current year was picked in year slider.
    #check if picked month are those not reached yet or current one
    # month in year not reached yet
    m = list(range(dash_function.dash_function.GetMinMonthWithoutPerf(),13))
    monthpicked = list(range(rangeslidermonth[0], rangeslidermonth[1] + 1))
    # print('m{0}'.format(m))
    # print('monthpicked{0}'.format(monthpicked))
    if checkboxyear:
        if datetime.datetime.today().year in rangeslideryear:
            prediction = True
            monthtopredict=m
            if checkboxmonth:
                if any(item in monthpicked for item  in m):
                    prediction = True
                    monthtopredict = set(m).intersection(set(monthpicked))
                else:
                    prediction = False
                    monthtopredict=None

        else:
            prediction = False
            monthtopredict=None

    elif checkboxmonth:
        if any(item in monthpicked for item  in m):
            prediction = True
            monthtopredict = set(m).intersection(set(monthpicked))
        else:
            prediction = False
            monthtopredict=None
    else:
        if datetime.datetime.today().year in rangeslideryear:
            prediction = True
            monthtopredict=m
        else:
            prediction = False
            monthtopredict=None
    
    #set headers for prediction
    if prediction:
        predictionvalue = dash_function.dash_function.GetMedian(df.copy(),aggregation,mill,monthtopredict)
        if aggregation == 'YEAR':
            headerprediction=["Prediction"]
        elif aggregation == 'MONTH':
            headerprediction=["Prediction"]*len(monthtopredict)
        elif aggregation == 'WINDMILL':
            headerprediction=["Prediction,"]*len(predictionvalue)
            
        data = [
            {'x': df[aggregation], 'y': df['_PLAN'],'z':df['_IS'], 'type': 'bar','text':header, 'name': 'Plan', 'marker':{'color':design['colors']['BarPlan']},'hovertemplate':"<extra></extra><b>%{text} </b> <br>PLAN: %{y} kWh", 'hoverinfo':'y'},
            {'x': df[aggregation], 'y': df['_IS'], 'type': 'bar','text':header, 'name': 'Is', 'marker':{'color':design['colors']['BarIs']},'hovertemplate':"<extra></extra><b>%{text} </b> <br>IS: %{y} kWh", 'hoverinfo':'y'},
            {'x': predictionvalue[aggregation], 'y': predictionvalue['_IS'], 'type': 'scatter','text':headerprediction, 'name': 'Prediction', 'marker':{'color':'rgb(255,0,127)'},'hovertemplate':"<extra></extra><b>%{text} </b> <br>IS: %{y} kWh", 'hoverinfo':'y'}
         ]
    else:
        data = [
            {'x': df[aggregation], 'y': df['_PLAN'],'z':df['_IS'], 'type': 'bar','text':header, 'name': 'Plan', 'marker':{'color':design['colors']['BarPlan']},'hovertemplate':"<extra></extra><b>%{text} </b> <br>PLAN: %{y} kWh", 'hoverinfo':'y'},
            {'x': df[aggregation], 'y': df['_IS'], 'type': 'bar','text':header, 'name': 'Is', 'marker':{'color':design['colors']['BarIs']},'hovertemplate':"<extra></extra><b>%{text} </b> <br>IS: %{y} kWh", 'hoverinfo':'y'},
        ]
    

    ################### end test #####################

    #######PIE CHART IN GRAPH5######
    dfwindmill = dash_function.dash_function.ExecuteQuery(
        [
            {
                "rows":"count(WM.WINDMILL) as NUMBER, WT.TYPE",
                "table":"Metabase.WIND_MILL WM inner join Metabase.WIND_TYPE WT on WM.TYPE = WT.ID",
                "where":[
                    {"Operator":"","WM.TYPE":">=2"},
                    {"Operator":"AND","WM.LOCATION":" IN(" + pielocation + ")"}
                        ],
                "groupby":"WT.TYPE"
            }
        ],"WindmillNumber",False
    )

    
    #######GAUGE IN GRAPH 4#########
    wheregauge.append({"Operator":"AND","WEP.ISPERFORMANCE":">0"})
    performancegauge = dash_function.dash_function.ExecuteQuery(
        [
            {
                "rows":"ifnull((sum(WEP.ISPERFORMANCE) / sum(WEP.PLANPERFORMANCE)) * 100,0) as _Performance",
                "table":"Metabase.WIND_ENERGY_PERFORMANCE WEP",
                "where":wheregauge,
            }
        ],"Performancegauge",False
    )

    return {##### return values for bar
            'data': data,
            'layout':{
                'title':'Energy Performance ' + "by " + str(aggregation),
                'showlegend':True,
                'legend':{'x':0,'y':"test"},
                'margin':{'l':40,'r':0,'t':40,'b':30},
                'plot_bgcolor':design['colors']['background'],
                'paper_bgcolor':design['colors']['background'],
                'fontcolor':design['colors']['text'],    
            }       
            },{#### return values for pie
                'data': [
                    {
                        'values': dfwindmill['NUMBER'],
                        'labels':dfwindmill['TYPE'],
                        'type': 'pie',
                        'name': 'windmilltype','marker':{'colors':design['colors']['PieType']}},
                
                ],
                'layout':{
                    'title':'Windmill ',
                    'showlegend':True,
                    'legend':{'x':0,'y':"test"},
                    'margin':{'l':40,'r':0,'t':40,'b':30},
                    'plot_bgcolor':design['colors']['background'],
                    'paper_bgcolor':design['colors']['background'],
                    'fontcolor':design['colors']['text'],    
            }
            },float(performancegauge["_Performance"]) #### return values for Gauge


##################################################
@app.callback(
    Output('windmill','options'),
    [Input('location','value')]
)
def GetWindmills(location):
# Get the windmills based on the first dropdown. 
    if str(location) == '1':
        logging.info("select WM.WINDMILL as NAME,WM.ID from Metabase.WIND_MILL WM where WM.LOCATION IN (2,3,4);")
        return dash_function.dash_function.GetLabel("select WM.WINDMILL as NAME,WM.ID from Metabase.WIND_MILL WM where WM.LOCATION IN (2,3,4);")

    else:
        logging.info("select WM.WINDMILL as NAME,WM.ID from Metabase.WIND_MILL WM where WM.LOCATION IN (" + str(location) + ");")
        return dash_function.dash_function.GetLabel("select WM.WINDMILL as NAME,WM.ID from Metabase.WIND_MILL WM where WM.LOCATION IN (" + str(location) + ");")
    

##################################################
@app.callback(
    Output('Invest','figure'),
    [Input('button','n_clicks'),
     Input('totalinvest','value')],
    [State('aggregation','value'),
     State('checkboxyear','value'),
     State('checkboxmonth','value'),
     State('rangeslideryear','value'),
     State('rangeslidermonth','value')
     ]
)
def UpdateInvestGraph(n_clicks,totalinvest,aggregation,checkboxyear,checkboxmonth,rangeslideryear,rangeslidermonth):
    # function to show the deposit and income of the year based on the values of the year/month slider

    # check if totalcheckbox is active
    # to show the total income when year slider doesn't show the first years anymore
    if totalinvest:
        where = [{"Operator":"","WI.WINDPARC":"=1"}]
    else:
        #create where statement
        where = dash_function.dash_function.CheckBoxYearMonth("WI",checkboxyear,None,rangeslideryear,None,[".YEAR",".MONTH"])
        #this is required if a second windparc is available. On this day(2020.08.26) it is not
        where.append({"Operator":"AND","WI.WINDPARC":"=1"})

    #create deposit query
    dfdeposit = dash_function.dash_function.ExecuteQuery(
            [
                {
                    "rows":"sum(WD.AMOUNT) as AMOUNT",
                    "table":"Metabase.WIND_DEPOSIT WD",
                    "where":[{"Operator":"","WD.WINDPARC":"=1"}]
                }
            ],"Invest",False
        )

    #create income query
    dfincome = dash_function.dash_function.ExecuteQuery(
            [
                {
                    "rows":"sum(WI.INCOME) as INCOME, sum(TAXES) as TAX",
                    "table":"Metabase.WIND_INCOME WI",
                    "where":where,
                }
            ],"Income",False
    )

    #determine of income - tax is lose or win
    outcome = dfincome['INCOME'] - dfincome['TAX']

    # return values of deposit and income
    return {
            'data': [
                {'x': 0,'y': dfdeposit['AMOUNT'], 'type': 'bar', 'name': 'Invest', 'marker':{'color': design['colors']['BarInvest']}},
                {'x': 0,'y': dfincome['INCOME'], 'type': 'bar', 'name': 'Income', 'marker':{'color': design['colors']['BarIncome']}},
                {'x': 0,'y': dfincome['TAX'],'type': 'bar', 'name': 'Tax', 'marker':{'color': design['colors']['BarTax']}},
                {'x': 0,'y': outcome,'type': 'bar', 'name': 'Win', 'marker':{'color': design['colors']['BarWin'] if outcome[0] >= 0 else design['colors']['BarLose']}}
            ],
            'layout':{
                'title':'Investment ',
                'showlegend':True,
                'legend':{'x':0,'y':"test"},
                'margin':{'l':40,'r':0,'t':40,'b':30},
                'plot_bgcolor':design['colors']['background'],
                'paper_bgcolor':design['colors']['background'],
                'fontcolor':design['colors']['text'],    
            }        
            }



##################################################
@app.callback(
    Output('Windspeed','figure'),
    [Input('button','n_clicks')],
    [State('aggregation','value'),
     State('checkboxyear','value'),
     State('checkboxmonth','value'),
     State('rangeslideryear','value'),
     State('rangeslidermonth','value')
     ]
)
def UpdateWindspeedGraph(n_clicks,aggregation,checkboxyear,checkboxmonth,rangeslideryear,rangeslidermonth):
    #function to show the Windpeed of the selected slider Year/month

    #create where statement
    where = dash_function.dash_function.CheckBoxYearMonth("",checkboxyear,checkboxmonth,rangeslideryear,rangeslidermonth,["YEAR(MW.DATE)","MONTH(MW.DATE)"]) 
    #declare variable
    data = []

    #create Windspeed query
    dfwindspeed = dash_function.dash_function.ExecuteQuery(
            [
                {
                    "rows":"avg(MW.WINDSPEED) as WINDSPEED,MONTH(MW.DATE) as MONTH, YEAR(MW.DATE) as YEAR",
                    "table":"Weather.MTS_WEATHER MW",
                    "where":where,
                    "groupby":"MONTH(MW.DATE), YEAR(MW.DATE)"
                }
            ],"Windspeed",False
        )
    #for each year create an own scatter and append to data
    for year in range(rangeslideryear[0],rangeslideryear[1] + 1):
        data.append({'x': dfwindspeed.loc[dfwindspeed["YEAR"] == year]["MONTH"],'y': dfwindspeed.loc[dfwindspeed["YEAR"] == year]["WINDSPEED"], 'type': 'scatter', 'name': 'Windspeed ' + str(year)})

    #return the values
    return {
            'data': data,
            'layout':{
                'title':'Windspeed by MONTH',
                'showlegend':True,
                'legend':{'x':0,'y':"test"},
                'margin':{'l':40,'r':0,'t':40,'b':30},
                'plot_bgcolor':design['colors']['background'],
                'paper_bgcolor':design['colors']['background'],
                'fontcolor':design['colors']['text'],    
            }        
            }

##################################################
##################################################
#start the server

#server = app.server # for production
if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port='8051')
