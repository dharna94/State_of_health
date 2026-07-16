# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

charging_data = pd.read_excel("charging_behaviour_MB7U8CLLFLJE30530.xlsx")
# discharging_data = pd.read_excel("charging_behaviour_MB7A8CLLTKJK30385.xlsx")
VIN = "MB7A8CLLTKJK30385"

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

##streamlit configurations
st.set_page_config(
    page_title="Cell Balancing Dashboard",
    layout='wide',
    initial_sidebar_state='auto'
)


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


#Scatterplot for Whr/km consumption during discharge

# plt.figure()
# sns.scatterplot(x="cyclenum",y="wh/km",data=discharging_data,s=40,cmap='copper')
# plt.title("Whr consumed per km",fontsize=24)
# plt.xlabel("Cycle Number",fontsize=22)
# plt.ylabel("Whr consumed / Distance covered", fontsize=22)
# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)
# plt.tight_layout()

# fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10,4))
# plt.bar(y_vars_soc,x_vars_soc)
# plt.bar(x_labels,y_vals)
# plt.show()


