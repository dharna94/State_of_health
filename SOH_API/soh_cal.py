import pandas as pd
import numpy as np
import statsmodels.api as sm
import configuration as conf
from SOH_API.soh_monthwise import Monthwise_SOH
import warnings
warnings.filterwarnings("ignore")

'''data suffeciency requirement for SOH calculation on regular data'''

def cal_soh(file_loc, vin):
    df = pd.read_csv(f"{file_loc}")
    print("original Shape: ", df.shape)
    df['avg_voltage'] = df[['bv1', 'bv2', 'bv3', 'bv4',
       'bv5', 'bv6', 'bv7', 'bv8', 'bv9', 'bv10',
       'bv11', 'bv12', 'bv13', 'bv14', 'bv15', 'bv16','bv17','bv18','bv19','bv20','bv21','bv22','bv23','bv24']].mean(axis=1)
    df['max_temp'] = df[['bt1','bt2','bt3','bt4']].max(axis=1)
    #filtering data 
    df = df[(df['state.1']==2) & (df['avg_voltage']>=3.36)]
    df['avg_voltage'] = round(df['avg_voltage'],2)
    print(df.shape)
    # print(df.cyclenum.unique())
    data = df.copy()

    ##checking for empty dataframe
    if(df.empty):
        print("empty dataframe")
        return 0
    print("should not come here")
    
    group_df = df.groupby(['vin','cyclenum', 'year', 'month'])

    global rows_list
    rows_list = []
    # VIN_name = df.vin.unique()[0]

    def aggregation_on_data(index):
        filtered_df = [group_df.get_group(x) for x in group_df.groups][index].copy()
        # print(filtered_df.cyclenum.unique())

        max_soc = filtered_df.soc.max()
        if(max_soc < 100):
            # print(VIN_name + "SOH can't be caluculated: Battery not reaching 100% SOC")
            return "SOH can't be caluculated: Battery not reaching 100% SOC"

        # filtered_df = filtered_df[filtered_df['avg_voltage']>=3.36]
        filtered_df.reset_index(inplace=True)
        y = filtered_df.loc[(filtered_df['avg_voltage'] == 3.36)].reset_index(drop = True)

        if y.shape[0]==0:
            # print("SOH can't be caluculated: Lowest_ah cannot be determined")
            return "SOH can't be caluculated: Lowest_ah cannot be determined"
        else:
            lowest_ah = y['ampherehour'][0]
            min_soc = y['soc'][0]
            start_voltage = y['avg_voltage'][0]
            lowest_ah
        x = filtered_df.loc[(filtered_df['soc'] == 100)].reset_index(drop = True)
        max_soc = x['soc'][0]
        highest_ah = x['ampherehour'][0]
        end_voltage = x['avg_voltage'][0]
        highest_ah
        # print("SOH can be calculated")

        #getting values for a row
        ah_consumed = highest_ah - lowest_ah
        filtered_df['intime'] =  pd.to_datetime(filtered_df['intime'], infer_datetime_format=True)
        date = filtered_df['intime'].min().date()
        end_time = filtered_df['intime'].max()
        state = filtered_df.state.min()
        temp = filtered_df['max_temp'].max()
        odometer = filtered_df['odometer'].max()
        vin = filtered_df['vin'].min()
        cyclenum = filtered_df['cyclenum'].min()

        ## column names : vin, cyclenum, date, end_time, state, odometer, min_soc, max_soc, start_voltage, end_voltage, ah_consumed, temp

        dict = {
            'vin' : vin,
            'cyclenum' : cyclenum,
            'date' : date,
            'end_time' : end_time,
            'state' : state,
            'odometer' : odometer,
            'min_soc' : min_soc,
            'max_soc' : max_soc,
            'start_voltage' : start_voltage,
            'end_voltage' : end_voltage,
            'ah_consumed' : ah_consumed,
            'temp' : temp
        }
        rows_list.append(dict)
        # print(rows_list)


    list(map(aggregation_on_data, range(group_df.ngroups)))    
    dict_df = pd.DataFrame(rows_list)
    final_df = dict_df

    """ Grouping for SOH calculation """
    dict_df = final_df
    dict_df = dict_df.dropna()
    # dict_df = dict_df[(dict_df['ah_consumed']>10)& (dict_df['ah_consumed']<75)]
    dict_df['month'] = dict_df['date'].apply(lambda x: str(x.month)) + "-" + dict_df['date'].apply(lambda x: str(x.year))

    X = dict_df['odometer']
    Y = dict_df['ah_consumed']
    print("printing x & y before constants")
    print(X)
    print(Y)
    
    if((X.empty) & (Y.empty)):
        print("empty odometer and ah_consumed")
        return 0

    results = sm.OLS(Y, sm.add_constant(X)).fit()

    params = results.params
    slope = params.odometer
    intercept = params.const

    # y = -0.0004*x + 44.3
    dict_df['up_y'] = (slope * dict_df['odometer'])  + intercept + 10
    dict_df['low_y'] = (slope * dict_df['odometer'])  + intercept - 10
    dict_df['to_be_taken'] = np.where((dict_df['ah_consumed']<=dict_df['up_y']) & (dict_df['ah_consumed']>=dict_df['low_y']), True, False)
    dict_df = dict_df[dict_df['to_be_taken'] == True]

    vin = vin[1:-1]
    print(vin)
    dict_df.to_csv(f"{conf.vin_soh_dict_loc}{vin}.csv")
    print("file created")
    filename = vin+".csv"
    print(filename)
    last_months_soh = Monthwise_SOH(conf.vin_soh_dict_loc, dict_df, vin, conf.soh_plots_loc)
    return last_months_soh