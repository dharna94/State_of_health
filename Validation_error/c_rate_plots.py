import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import streamlit as st
pd.set_option('display.max_columns', None)

df = pd.read_csv('c_rate&cell_deviation_reg_data.csv')

def run():
    options = df['vin'].unique().tolist()

    selected_options = st.selectbox('Select VINs',options)

    df_filtered = df[df["vin"] == selected_options]

    print(df_filtered.columns)

    df_filtered = df_filtered[(df_filtered['state1']==3) & (df_filtered['battcurrent']<=0)]
    df_filtered['calc_current'] = df_filtered['battcurrent']/144
    group_df = df_filtered.groupby(['vin','state','cyclenum']).agg({'calc_current':'mean', 'odometer':'min', 'intime':'min'}).reset_index()

    vin = df_filtered.vin.unique()[0]
    filtered_df = df_filtered[df_filtered['calc_current'] <= -0.01]
    filtered_df = filtered_df.sort_values('intime').reset_index(drop = True)
    filtered_df['intime'] = pd.to_datetime(filtered_df['intime'], infer_datetime_format=True)
    filtered_df['date'] = filtered_df['intime'].apply(lambda x : str(x.day)+'-'+str(x.month)+'-'+str(x.year))
    fig = px.line(filtered_df, x="date", y="calc_current", title=vin+" battery current TREND")
    # fig.show()
    st.plotly_chart(fig)

    # list(map(plot, range(vin_group.ngroups)))