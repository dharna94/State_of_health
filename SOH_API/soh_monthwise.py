# import csv
import csv
import numpy as np
import pandas as pd
import plotly_express as px

name=[]

Initial_Ah = 56.3
Const = 1    #input ('constant factor')

def Monthwise_SOH(file_loc, dictdf, vin, soh_plots_loc):
    print("In monthwise file...")
    # file_to_read = pd.read_csv(f'{filename}.csv')
    file_to_read = dictdf

    file_to_read["date"] = pd.to_datetime(file_to_read["date"])
    Month_Avg_Partial_Ah = file_to_read.groupby([file_to_read.date.dt.year,file_to_read.date.dt.month])['ah_consumed'].mean().to_frame()
    Month_Avg_Celltemp   = file_to_read.groupby([file_to_read.date.dt.year,file_to_read.date.dt.month])['temp'].mean().to_frame()
    Month_end_Odometer   = file_to_read.groupby([file_to_read.date.dt.year,file_to_read.date.dt.month])['odometer'].last().to_frame()
    
    ## SOH Calculations
    nop = len(Month_Avg_Partial_Ah)
    Relative_Ah=[]
    SOH_Cal=[]
    SOH_km_Avg=[]
    Tsoh=[]
    IC=99.5
    A=168183.5
    B=-2374.74


    for q in range (0,nop):
        Tsoh.append(float(Month_Avg_Celltemp.iloc[q])+273)
        ExpF=np.exp(B/Tsoh[q])
        Relative_Ah.append((file_to_read.ah_consumed.max()-float(Month_Avg_Partial_Ah.iloc[q]))/(file_to_read.ah_consumed.max()))
        if(Tsoh[q]>308):
            SOH_Cal.append(99.5-(0.47*Const*A*ExpF*Relative_Ah[q]))
        else:
            SOH_Cal.append(99.5-(Const*A*ExpF*Relative_Ah[q]))
        ## recursive calculation
        if q==0:
            SOH_km_Avg.append(SOH_Cal[0])
        # if q==0 and k==3:
        #     SOH_km_Avg[0]=99.5
        if q!=0:
            Aterm = float(float(Month_end_Odometer.iloc[q-1])*SOH_km_Avg[q-1])
            Bterm = (float(Month_end_Odometer.iloc[q])-float(Month_end_Odometer.iloc[q-1]))*SOH_Cal[q]
            Cterm = float(Month_end_Odometer.iloc[q])
            SOH_km_Avg.append((Aterm+Bterm)/Cterm)
            
            
    newlist=pd.DataFrame({'Avg_Cell_temp_k':Tsoh,'Relative_Partial_Ah':Relative_Ah,'SOH Calc':SOH_Cal,
                        'SOH_km_Avg':SOH_km_Avg},
                        index=Month_Avg_Celltemp.index)
    Month_Avg = pd.concat([Month_Avg_Partial_Ah,Month_Avg_Celltemp,Month_end_Odometer,newlist],axis=1)
    print(Month_Avg)

    Month_Avg.to_csv(f"{file_loc}{vin}_output.csv")
    print("Final Output created...")

    """ PLotting SOH curve with time """
    df = pd.read_csv(f"{file_loc}{vin}_output.csv")
    print(df.columns)
    df.columns = ['year', 'month', 'ah_consumed', 'temp', 'odometer', 'Avg_Cell_temp_k', 'Relative_Partial_Ah', 'SOH Calc', 'SOH_km_Avg']

    last_soh_vin = vin
    last_soh_year = df.iloc[-1]["year"]
    last_soh_month = df.iloc[-1]["month"]
    last_soh_value = df.iloc[-1]['SOH_km_Avg']
    temp_list = [[last_soh_vin, last_soh_year, last_soh_month, last_soh_value]]

    # opening the csv file in 'w+' mode    
    file = open('last_month_soh_new.csv', 'a', newline ='')
    # writing the data into the file    
    with file:
        write = csv.writer(file)
        write.writerows(temp_list)
        
    file.close()

    print("last_soh", last_soh_value)


    print(df.columns)
    data = df.copy()
    data['year_month'] = (data['year']).astype(str)+"-"+((data['month']).astype(str)).str.zfill(2)
    data['SOH_km_Avg'] = round(data['SOH_km_Avg'], 2)
    fig = px.line(data, x="year_month", y="SOH_km_Avg", title='SOH: ' + vin, markers=True, text="SOH_km_Avg")
    # Edit the layout
    fig.update_layout(xaxis_title='Month',
                    yaxis_title='SOH')
    fig.update_traces(textposition="top center", textfont_size=10)
    fig.write_html(f"{soh_plots_loc}{vin}.html")
    
    return last_soh_value

