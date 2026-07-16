# -*- coding: utf-8 -*-

import pandas as pd
import glob
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from functools import reduce


def run():
    df = pd.read_csv('c_rate&cell_deviation_reg_data.csv')

    charge_number_profile = [20,21,22,24,23,26,28,29,40,41,42,43,46,47,48]
    fastcharge_profile = ['FastCharge:C1','FastCharge:C2',
                            'FastCharge:CC','FastCharge:CH','FastCharge:CI','FastCharge:CB','FastCharge:CP',
                            'FastCharge:CQ','FastCharge:CT']

    voltage_indexes = range(22,38)

    df['avgcelltemp'] = df[['bt1','bt2','bt3','bt4']].mean(axis=1)
    df['maxcelltemp'] = df[['bt1','bt2','bt3','bt4']].max(axis=1)

    ##adding dropdown streamlit part

    options = df['vin'].unique().tolist()

    selected_options = st.selectbox('Select VINs',options)

    df_filtered = df[df["vin"] == selected_options]

    def plotting(vin_data, VIN):

        vin_data = vin_data.loc[vin_data['state'].isin(charge_number_profile)]
        
        vin_data['intime_ist'] = pd.to_datetime(vin_data['intime'])
        
        intime_start = vin_data.groupby(["odometer"])["intime_ist"].first().to_frame()
        intime_end =vin_data.groupby(["odometer"])["intime_ist"].last().to_frame()
        
        charge_duration = ((intime_end['intime_ist']-intime_start['intime_ist']).dt.total_seconds()/3600).to_frame()
        
        soc_start = vin_data.groupby(["odometer"])["soc"].first().to_frame()
        soc_end = vin_data.groupby(["odometer"])["soc"].last().to_frame()
        
        cyclenum = vin_data.groupby(["odometer"])["cyclenum"].first().to_frame()
        
        vin_data["maxv"] = vin_data[['bv1','bv2','bv3','bv4','bv5','bv6',
            'bv7','bv8','bv9','bv10','bv11','bv12','bv13','bv14','bv15','bv16']].max(axis=1)
        vin_data["minv"] = vin_data[['bv1','bv2','bv3','bv4','bv5','bv6',
            'bv7','bv8','bv9','bv10','bv11','bv12','bv13','bv14','bv15','bv16']].min(axis=1)

        vin_data["maxv_cellno"] = vin_data[['bv1','bv2','bv3','bv4','bv5','bv6',
            'bv7','bv8','bv9','bv10','bv11','bv12','bv13','bv14','bv15','bv16']].idxmax(axis=1)
        vin_data["minv_cellno"] = vin_data[['bv1','bv2','bv3','bv4','bv5','bv6',
            'bv7','bv8','bv9','bv10','bv11','bv12','bv13','bv14','bv15','bv16']].idxmin(axis=1)
        
        maxv_EOC = vin_data.groupby(["odometer"])["maxv"].last().to_frame()
        minv_EOC = vin_data.groupby(["odometer"])["minv"].last().to_frame()
        
        deltaV_EOC = (maxv_EOC['maxv'] - minv_EOC['minv']).to_frame()
        deltaV_EOC.columns = ["deltav_EOC"]
        
        maxv_cellno_EOC = vin_data.groupby(["odometer"])["maxv_cellno"].last().to_frame()
        minv_cellno_EOC = vin_data.groupby(["odometer"])["minv_cellno"].last().to_frame()
        
        
        soc_delivered = soc_end - soc_start
        
        state = vin_data.groupby(["odometer"])["state"].first().to_frame()
        
        avg_temperature = vin_data.groupby(["odometer"])["avgcelltemp"].first().to_frame()
        max_temperature = vin_data.groupby(["odometer"])["maxcelltemp"].first().to_frame()
        
        avg_temp_end = vin_data.groupby(["odometer"])["avgcelltemp"].last().to_frame()
        max_temp_end = vin_data.groupby(["odometer"])["maxcelltemp"].last().to_frame()
        
        kwh_start = vin_data.groupby(["odometer"])["kwh"].first().to_frame()
        kwh_end = vin_data.groupby(["odometer"])["kwh"].last().to_frame()
        
        power_added = kwh_end - kwh_start
        
        ah_start = vin_data.groupby(["odometer"])["ampherehour"].first().to_frame()
        ah_end = vin_data.groupby(["odometer"])["ampherehour"].last().to_frame()
        
        ah_added = ah_end - ah_start
        
        data2 = vin_data[vin_data["soc"]==100.0]
        
        intime_at_100_soc = data2.groupby(["odometer"])["intime_ist"].first().to_frame()
        maxv_100SOC = data2.groupby(["odometer"])["maxv"].first().to_frame()
        minv_100SOC = data2.groupby(["odometer"])["minv"].first().to_frame()
        
        deltaV_100SOC = (maxv_100SOC['maxv'] - minv_100SOC['minv']).to_frame()
        deltaV_100SOC.columns = ['deltaV_100SOC']
        
        maxv_cellno_100SOC = data2.groupby(["odometer"])["maxv_cellno"].first().to_frame()
        minv_cellno_100SOC = data2.groupby(["odometer"])["minv_cellno"].first().to_frame()
        
        
        time_since_fullcharge = ((intime_end['intime_ist']-intime_at_100_soc['intime_ist']).dt.total_seconds()/3600).to_frame()
        
        cb_data = vin_data[vin_data['state'].isin([24])]
        
        cb_startime = cb_data.groupby(["odometer"])["intime_ist"].first().to_frame()
        cb_endtime = cb_data.groupby(["odometer"])["intime_ist"].last().to_frame()
        
        charge_hour = vin_data.groupby(["odometer"])["intime_ist"].first().dt.hour.to_frame()
        
        cellbalancing_time = ((cb_endtime['intime_ist']-cb_startime['intime_ist']).dt.total_seconds()/3600).to_frame()
        
        
        combined_frames=[charge_duration,soc_start['soc'],soc_end['soc'],soc_delivered,intime_start,intime_end,
                        state,kwh_start,kwh_end,power_added,cyclenum,avg_temperature,max_temperature,avg_temp_end,max_temp_end,
                        ah_start,ah_end,ah_added,
                        intime_at_100_soc,time_since_fullcharge,maxv_EOC,minv_EOC,maxv_cellno_EOC,minv_cellno_EOC,
                        maxv_100SOC,minv_100SOC,maxv_cellno_100SOC,minv_cellno_100SOC,deltaV_EOC, deltaV_100SOC,
                        cb_startime,cb_endtime,cellbalancing_time,charge_hour
                        ]
        
        df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['odometer'],
                                                    how='outer'), combined_frames)
        
        df_merged.columns = ['charge_duration','soc_start','soc_end','soc_added','intime_start','intime_end',
                            'chargeType','kwh_start','kwh_end','power_added','cyclenum','avg_temp_start','max_temp_start',
                            'avg_temp_end','max_temp_end','ah_start','ah_end','ah_added',
                            'time_at_100_soc','duration_after_100_soc','maxv_EOC','minv_EOC','maxv_EOC_cellno',
                            'minv_EOC_cellno','maxv_100SOC','minv_100SOC','maxv_100SOC_cellno','minv_100SOC_cellno',
                            'deltaV_EOC','deltaV_100SOC','cb_startime','cb_endtime','cb_duration','charge_hour']
        
        df_merged = df_merged[(df_merged['charge_duration']>0) & (df_merged['charge_duration']<14)] 
        df_merged = df_merged[df_merged['soc_added']>0].reset_index()
        
        total_cycles = df_merged.charge_duration.count()
        total_fullcharge_cycles = df_merged[df_merged['soc_end']==100]
        no_fullchg_cycles = total_fullcharge_cycles.charge_duration.count()
        
        # df_merged.to_excel('charging_behaviour_'+i+'.xlsx')
        print(df_merged)
        print(df_merged.columns)
        charging_data = df_merged.copy()
        print(charging_data.columns)
        total_chg_cycles = charging_data['odometer'].count()  

        fullchg_cycles = charging_data[charging_data["soc_end"]>=99]

        fullcharge_cycles_count = fullchg_cycles["soc_end"].count()

        cycles_cb_attempted = charging_data["cb_duration"].count()

        #bar plot for Charging Summary
        x_labels = ["Charge cycles","Fullcharge cycles","Cycles CB attempted"]
        y_vals = [total_chg_cycles,fullcharge_cycles_count,cycles_cb_attempted]

        #changes the background style of chart, can be changed to different styles
        plt.style.use('fast')

        print(y_vals)
        print(x_labels)



        ## defining streamlit container
        with st.container():
            c1, c2, c3 = st.columns((1,1,1))

        with st.container():
            c4, c5 = st.columns((1,1))


        plt.figure(figsize=(15,10))
        plt.bar(x_labels,y_vals)
        plt.title("Charging Summary " + VIN,fontsize=24)
        plt.xlabel("No. of cycles",fontsize=20)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.tight_layout()
        c1.pyplot(plt)
        plt.savefig(f'plots/{VIN}_Charging Summary.png')
        plt.show() 
        plt.close()
        # plt.savefig(f'{VIN}+_Charging Summary.png')

        #Buckets for SOC's at which the charging begins
        cycles_lt20 = charging_data["soc_start"].agg(lambda x: x[x<20].count()) #<20%
        cycles_gt21_50 = (charging_data[(charging_data.soc_start > 21) & (charging_data.soc_start < 50)]).shape[0] #21-50%
        cycles_gt51_80 = (charging_data[(charging_data.soc_start > 51) & (charging_data.soc_start < 80)]).shape[0] #51-80%
        cycles_gt80 = charging_data["soc_start"].agg(lambda x : x[x>=80].count()) #>80%

        #bar plot for SOC at which charging starts
        x_vars_soc = [cycles_lt20,cycles_gt21_50,cycles_gt51_80,cycles_gt80]
        y_vars_soc = ["<20%","21 - 50%","51 - 80%",">80%"]

        plt.figure(figsize=(15,10))
        plt.bar(y_vars_soc,x_vars_soc)
        plt.title("SOC(%) at which charging begins " + VIN,fontsize=24)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.xlabel("SOC Range",fontsize=22)
        plt.ylabel("No. of cycles",fontsize=22)
        plt.tight_layout()
        c2.pyplot(plt)
        plt.savefig(f'plots/{VIN}_SOC(%) at which charging begins.png')  
        plt.show() 
        plt.close()


        #bar plots for time of the day when full charge cycle starts
        plt.figure(figsize=(20,15))
        #countplot gets the count for each value in the column and displays the bar chart
        ax = sns.countplot(x="charge_hour",data=fullchg_cycles,palette="tab10",
                        order=fullchg_cycles["charge_hour"].value_counts().index) #arrange the bars in desc order
        plt.title("Hour of the day when full charge is done " + VIN,fontsize=24)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.xlabel("Time of the day",fontsize=22)
        plt.ylabel("Number of cycles",fontsize=22)
        plt.tight_layout()
        c4.pyplot(plt)
        plt.savefig(f'plots/{VIN}_Hour of the day when full charge is done.png')  
        plt.show()
        plt.close()

        cb_duration_lt1 = charging_data["cb_duration"].agg(lambda x: x[x<1].count()) #<20%
        cb_duration_1to2 = (charging_data[(charging_data.cb_duration > 1) & (charging_data.cb_duration < 2)]).shape[0] #21-50%
        cb_duration_2to3 = (charging_data[(charging_data.cb_duration >= 2) & (charging_data.cb_duration < 3)]).shape[0] #51-80%
        cb_duration_3to4 = (charging_data[(charging_data.cb_duration >= 3) & (charging_data.cb_duration < 4)]).shape[0] #51-80%
        cb_duration_gt4 = charging_data["cb_duration"].agg(lambda x : x[x>=4].count()) #>80%


        x_labels_cb = ["<1 Hour","1 - 2 Hours","2 - 3 Hours","3 - 4 Hours","4+ Hours"]
        y_vals_cb = [cb_duration_lt1,cb_duration_1to2,cb_duration_2to3,cb_duration_3to4,cb_duration_gt4]

        plt.figure(figsize=(15,10))
        ax = plt.bar(x_labels_cb,y_vals_cb)
        plt.title("Cell Balancing Duration " + VIN,fontsize=24)
        #plt.xticks(range(0,max(y_vals_cb)+5,5))
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.xlabel("No. of Cycles",fontsize=22)
        plt.ylabel("Duration",fontsize=22)
        plt.tight_layout()
        c3.pyplot(plt)
        plt.savefig(f'plots/{VIN}_Cell Balancing Duration.png')  
        plt.show() 
        plt.close()

        print(type(fullchg_cycles))
        fullchg_cycles = fullchg_cycles[(fullchg_cycles['deltaV_EOC']<1) & (fullchg_cycles['deltaV_100SOC']<1)]
        print(fullchg_cycles['deltaV_EOC'])

        #Scatterplots for deltaV at EOC and 100% SOC and corresponding CB duration
        plt.figure(figsize=(20,15))
        ax1 = plt.subplot(211)
        ax1 = sns.scatterplot(x="odometer",y="deltaV_100SOC",data=fullchg_cycles,label="deltaV at 100%SOC",s=35)
        sns.scatterplot(x="odometer",y="deltaV_EOC",data=fullchg_cycles, label="deltaV after CB",s=35)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.legend(fontsize=18)
        #create a secondary Y axis to plot CB duration
        #ax2 = ax1.twinx()
        ax2 = plt.subplot(212, sharex = ax1)
        ax2.scatter('odometer', 'cb_duration', data=fullchg_cycles, marker='o',c="green",
                alpha=0.7)
        plt.suptitle("Voltage Difference v/s Cell Balancing Duration " + VIN,fontsize=24)

        ax1.set_xlabel("Odometer",fontsize=22)
        ax1.set_ylabel("Delta V (V)",fontsize=22)
        ax2.set_ylabel("Cell Balancing Time (Hours)",fontsize=22)
        ax2.set_ylim(0,5)
        plt.tight_layout()
        c5.pyplot(plt)
        plt.savefig(f'plots/{VIN}_Voltage Difference_Cell Balancing Duration.png')  
        plt.show() 
        plt.close()


    plotting(df_filtered, selected_options)