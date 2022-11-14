import streamlit as st
import pandas as pd
import random
import geopandas as gpd
from shapely import wkt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Cities in Action for Learning Lab (CALL)")
st.subheader("Discover CALL's projects, pilots, and network.")

df = pd.read_csv('data/City_pilots.csv',
                 delimiter=';',
                 encoding='unicode_escape')

dfalluvial = pd.read_csv('data/Network_polimi.csv',
                         delimiter=';',
                         encoding='iso-8859-1')
dfA = dfalluvial.loc[:, ['Project', 'Type', 'Name']]  # 'Country',

dfP = pd.read_csv('data/Projects.csv',
                  delimiter=';',
                  encoding='iso-8859-1',
                  index_col='Project')

dfP['Start_Date'] = pd.to_datetime(dfP['Start_Date'])
dfP['End_Date'] = pd.to_datetime(dfP['End_Date'])

# Columns to filters
df_filtcol = ['Project',
              # 'City',
              # 'Country',
              ]

user_cat_input = st.multiselect(
    'Select one or many projects',
    df.Project.unique(),
    default=df.Project.unique())

df = df[df["Project"].isin(user_cat_input)]

# PILOT MAP --------------------------------------

if len(user_cat_input) == 1:
    dfP_text = dfP.loc[user_cat_input, :]
    st.subheader(user_cat_input[0])
    st.markdown(dfP_text.Complete_name[0])
    st.markdown(dfP_text.Website[0])

else:
    dfP = dfP[dfP.index.isin(user_cat_input)]
    dfP = dfP.sort_values(by=['Start_Date'], ascending=False)
    fig = px.timeline(dfP, "Start_Date", "End_Date",
                      y=dfP.index,
                      color=dfP.index)
    fig.update_layout(  # title_text="Gantt dyagram",
                      font_size=13,
                      height=500,
                      )
    fig.update_layout(showlegend=False)
    for i in range(len(dfP.index)):
        fig.add_hline(y=i, line_width=0.5, line_color="white", opacity=1)
        i += 2
    fig.update_xaxes(dtick="M24")
    fig.update_yaxes(categoryarray=dfP.index)
    st.subheader('Projects timeline')
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------

# Select columns to view and to exclude
dfex_col = df.loc[:, df.columns.isin(df_filtcol)]
# Count filtered values
dfcount = str(dfex_col.Project.count())
# Run in streamlit
st.subheader('Pilot cities: '+dfcount)

# PILOT MAP --------------------------------------

df['geometry'] = df['Coord'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, crs='WGS84')

# Select indices to show in map
nofiltcolmap = df_filtcol+(['Coord'])
filtcolmap = ['Project', 'City', 'Country']

option = 'Project'

gdf = gdf.sort_values(by=[option])

fig = px.scatter_mapbox(gdf,
                        lat=gdf.geometry.y,
                        lon=gdf.geometry.x,
                        hover_name='City',
                        color=gdf[option],
                        size="count_city",
                        size_max=15,
                        zoom=2.2)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.update_layout(mapbox_style="carto-positron")

st.plotly_chart(fig, use_container_width=True)

# ALLUVIAL ---------------------------------------

dfA = dfA[dfA["Project"].isin(user_cat_input)]

network_input = st.multiselect(
    'Select network typology',
    dfA.Type.unique(),
    default=dfA.Type.unique())

dfA = dfA[dfA["Type"].isin(network_input)]
# Alias name for columns
d_alluvial = {"Project": "Project", "Name": "Network", "Type": "Typology"}
dfA = dfA.rename(columns=d_alluvial)

df_col_noid = dfA.columns.to_list()
dfA["id"] = dfA.index

# groups has all the combinations of columns
groups = dfA.groupby(df_col_noid).agg({'id': 'count'}).reset_index()

colnum = len(df_col_noid)
list_ = []
list_fsize = []
coln = 0
for col in range(colnum-1):
    link = groups.groupby([dfA.columns[coln], dfA.columns[coln+1]]).agg({'id': 'sum'}).rename({'id': 'count'}).reset_index()
    list_.append(link)
    coln += 1

# Ripeto l'operazione solamente per creare il dizionario dimensione labels
coln = 0
for col in range(colnum):
    f_size_count = groups.groupby(dfA.columns[coln]).agg({'id': 'sum'}).rename({'id': 'count'}).reset_index()
    list_fsize.append(f_size_count)
    coln += 1

names = []  # names contains all the labels of our nodes.
count_dict = {}  # will contain all info of value list
source_list = []  # will contain all info of source
target_list = []  # will contain all info of target

for i in range(0, len(list_)):
    cols = list_[i].columns  # contains columns for our dataframe
    for x, y, z in zip(list_[i][cols[0]], list_[i][cols[1]], list_[i][cols[2]]):
        if(x not in names):
            names.append(x)  # appends in names
        count_dict[x, y] = z
        source_list.append(x)
        target_list.append(y)

# Now we add labels into name for the last column targets
for v in target_list:
    if v not in names:
        names.append(v)

# list_fsize
fsize = []
count_fsize = []

for i in range(0, len(list_fsize)):
    cols = list_fsize[i].columns
    for x, y in zip(list_fsize[i][cols[0]], list_fsize[i][cols[1]]):
        if(x not in fsize):
            fsize.append(x)
        count_fsize.append(y)

for v in target_list:
    if v not in fsize:
        fsize.append(v)

all_numerics = {}
for i in range(0, len(names)):
    all_numerics[names[i]] = i

dfitems = []
for i in df_col_noid:
    dfitems.extend(dfA[i].unique())

color_dict = {}
color_dict_link = {}
for i in dfitems:
    r = str(random.randint(0, 255))
    g = str(random.randint(0, 255))
    b = str(random.randint(0, 255))
    color_dict[i] = "rgba(" + r + "," + g + "," + b + ",0.8)"
    # color_dict_link[i] = "rgba(" + r + "," + g + "," + b + ",0.4)"
    color_dict_link[i] = "rgb(" + r + "," + g + "," + b + ")"

# Plotting, everything is the same as last with added colors and labels

fig = go.Figure(data=[go.Sankey(
    node=dict(
      thickness=7,
      line=dict(color=None, width=0.01),
      label=names,
      # Adding node colors,have to split to remove the added suffix
      color=[color_dict[x] for x in names],),
    textfont=dict(
      size=11,
      color="black"),
    link=dict(
      source=[all_numerics[x] for x in source_list],
      target=[all_numerics[x] for x in target_list],
      value=[count_dict[x, y] for x, y in zip(source_list, target_list)],
      # Adding link colors,have to split to remove the added suffix
      # color = [color_dict_link[x] for x in target_list]
    ),)])

dfA_network = dfA.Network.unique().size

if dfA_network <= 20:
    alluvial_h = 500
elif 20 < dfA_network <= 50:
    alluvial_h = 700
elif 50 < dfA_network <= 80:
    alluvial_h = 900
else:
    alluvial_h = 1200

fig.update_layout(  # title_text="<b>Alluvial diagram</b><br>Play with data",
                  font_size=18,
                  # width=1000,
                  height=alluvial_h,
                  margin=dict(t=210, l=90, b=20, r=30)
                  )

# ------------------------------------------------

dfAcount = str(dfA_network)
# Run in streamlit
st.subheader('Networks: '+dfAcount)
# st.markdown(dfA.Network.unique())
st.plotly_chart(fig, use_container_width=True)
