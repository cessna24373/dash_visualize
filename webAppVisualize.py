import plotly.express as px
from dash import dcc,html,Dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd
import re

numCol=50
days=31
data=[]
for h in range(days):
    for i in range(24):
        for j in np.arange(0,60,5):
            data.append(f"2022/12/{h+1:02} {i:02}:{j:02}:00")
data=pd.to_datetime(data)
locs=np.random.uniform(5,15,numCol)
sds=np.random.uniform(3,5,numCol)
dfs=[]
for day in range(1,days+1):
    a=np.random.normal(locs,2).reshape(1,-1)
    b=np.random.uniform(-5,5,a.shape)+locs.reshape(1,-1)
    x=np.linspace(-np.pi,np.pi,24*12).reshape(-1,1)
    c=a*np.cos(x)+b
    c=c+np.random.uniform(-5,5,c.shape)
    dfs.append(pd.DataFrame(c))
original=pd.concat(dfs,axis=0)
original.index=data

widths=pd.DataFrame(np.random.uniform(1,3,original.shape),index=data)
df=pd.concat([original,widths],axis=1)                
cols=[f"col{str(i)}_{j}" for j in ["ave","width"] for i in range(50) ]
df.columns=cols
df["day"]=df.index.day
df["hour"]=df.index.hour
daysall=sorted(set(df["day"]))

cols=[re.sub(r"col(\d+)_.*",r"\1",col) for col in cols]

# ➌ Dashインスタンスの作成
app = Dash(__name__)
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
drop=html.Div([
    dcc.Dropdown(cols, value=cols[0], id='dropdown1',multi=True),
])
dropday=html.Div([
    dcc.Dropdown(daysall, daysall[0], id='dropday'),
])

# ➍ レイアウトの作成
app.layout = dbc.Container([
                dbc.Row([
                    dbc.Col([html.H3("センサ解析")],width=2),
                    dbc.Col([dcc.Graph(id="glance"),],width=10)
                    ]),
                dbc.Row([
                    dbc.Col([
                        html.Div("センサー番号"),html.Div(drop)],width=2),
                    dbc.Col([dcc.Graph(id="gap_all"),],width=10),
                    ]),
                dbc.Row([
                    dbc.Col([
                    html.Div("日付"),html.Div(dropday),],width=2),
                dbc.Col([dcc.Graph(id="oneday"),],width=10)
                    ])
                ])

# ➎ コールバックの作成
@app.callback(Output("glance", "figure"),
              Output("gap_all", "figure"), 
              Output("oneday", "figure"),
              Input("dropdown1","value"),
              Input("dropday","value"),
              )
def update_graph(list1,day):
    if type(list1)==int:
        list1=[list1]
    df["hour"]=df.index.hour
    df["day"]=df.index.day    
    list2=[f"col{item}_ave" for item in list1]
    mm=df[list2+["day"]].groupby("day",as_index=False).mean()
    g1=px.line(mm,x="day",y=list2,title="Monthly temp")    
    mmh=df.loc[df["day"]==day,list2+["hour"]].groupby("hour",as_index=False).mean()
    g2=px.line(mmh,x="hour",y=list2,title="daily temp")

    mm=df.groupby("day",as_index=False).mean()
    df2=mm.melt(id_vars=["day"])
    df3=df2[df2.variable.str.contains("ave")]
    df3["facet"]=(df3.index/(31*20)).astype(int)
    df3=df3.iloc[:310,:]
    g0 = px.violin(df3, y="value", x="variable",box=True, points=None)
    return (g0,g1,g2)


if __name__ == "__main__":
    app.run_server(debug=True)
    pass
