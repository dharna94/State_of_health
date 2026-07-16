import os

"""----------------------------------------Athena and S3 Util----------------------------------------"""
db_name = 'evehicle-data-parquet-prod'
S3_bucket_loc = 's3://sampleautomation'
bucket_folder = 'out4'

bucket_name = 'sampleautomation'
output_loc_s3 = S3_bucket_loc+'/'+bucket_folder

"""------------------------------------------ Constants -------------------------------------------"""
IC = 99.5
A = 168183.56
B = 2374.74

""" -----vin specifications -----"""
odo = 32603
cycle = 1009

"""---------------------------------------- SOH Parameters ----------------------------------------"""
download_s3_loc_reg = "/Users/dharnagoyal/Desktop/DharnaGoyal/SOH/SOH_API/data/" 
vin_soh_dict_loc = "/Users/dharnagoyal/Desktop/DharnaGoyal/SOH/SOH_API/VIN_files/"
soh_plots_loc = "/Users/dharnagoyal/Desktop/DharnaGoyal/SOH/SOH_API/SOH_plots/"