import sys
import os, csv
SCRIPT_DIR = r"/Users/dharnagoyal/Desktop/DharnaGoyal/SOH/SOH_API/Utils" 
sys.path.append(os.path.dirname(SCRIPT_DIR)) 
from Utils.boto3Client import athena_client, s3_client
from Utils.s3_util import S3_util
from Utils.athena_util import Athena_util 
from Queries.query import queries
import configuration
from SOH_API.soh_cal import cal_soh
from flask import jsonify
import datetime as dt
from celery import Celery, group
from celery.utils.log import get_task_logger
import pandas as pd

df = pd.DataFrame()


CELERY_IMPORTS = [
    'app_name.tasks',
]

logger = get_task_logger(__name__)

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0', include=["SOH_API.celery_worker"])

# Creating obj for classes
au = Athena_util()
su = S3_util()

@celery.task()
def get_data(vin):
    def get_query_result(athena_client, s3_client, query, file_name, vin):
        # Query Athena and download the result to local

        response = au.query_athena(athena_client, query, configuration.db_name, configuration.output_loc_s3)
        date = "_"+dt.datetime.now().strftime("%d%m%Y")
        vin = vin[1:len(vin) - 1]
        download_s3_loc_reg_data = configuration.download_s3_loc_reg +  vin +"_"+ file_name + date +"_data.csv"
        print("Download Location...", download_s3_loc_reg_data)

        su.get_file_from_s3(athena_client, response, s3_client, download_s3_loc_reg_data, configuration.bucket_name, configuration.bucket_folder)
        print("Successfully downloaded", file_name)
        return download_s3_loc_reg_data

    print("fetching data for", vin)
    """ Getting regular data """
    final_query = queries(vin)
    print(final_query)
    file_loc = get_query_result(athena_client, s3_client, final_query, "soh", vin)

    """ state health """
    # vin = vin[1:len(vin) - 1]
    # print(vin)
    print(os.getcwd())
    # file_loc = f"../data/{vin}_soh_28112022_data.csv"
    last_months_soh = cal_soh(file_loc, vin)
    print("Last recorded", last_months_soh)
    print(type(last_months_soh))

    # temp_list = [[vin, last_months_soh]]

    global df
    df = df.append({'Vin' : vin, 'SOH' : last_months_soh}, ignore_index = True)

    file = open('latest_soh_celery.csv', 'a', newline ='')
    # writing the data into the file    
    with file:
        write = csv.writer(file)
        write.writerows(temp_list)
        
    file.close()

    # return jsonify({"Last SOH": float(last_months_soh)})
    return "Excel Created!"

@celery.task()
def group_vins(vinlist):
    logger.info('Got Request - Starting work ')
    job = group(get_data.s(i) for i in vinlist)()
    print(job)
    logger.info('Work Finished ')
    global df
    df.to_csv("hey_trying.csv")
    