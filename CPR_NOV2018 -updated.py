#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
plt.rc('figure', figsize = (10,6))
np.set_printoptions(precision =4, suppress=True)
pd.options.display.max_rows = 10


# Import two datasets
colnames = ["LOAN_ID", "ORIG_CHN", "Seller.Name", "ORIG_RT", "ORIG_AMT", "ORIG_TRM", "ORIG_DTE","FRST_DTE", "OLTV", 
            "OCLTV", "NUM_BO", "DTI", "CSCORE_B", "FTHB_FLG", "PURPOSE", "PROP_TYP","NUM_UNIT", "OCC_STAT", 
            "STATE", "ZIP_3", "MI_PCT", "Product.Type", "CSCORE_C", "MI_TYPE", "RELOCATION_FLG"]
Data_A = pd.read_table('D:/1-Intern/Project_1/2018Q1/Acquisition_2018Q1.txt', 
                       sep = '|', header = None, names = colnames)

colnames_P = ["LOAN_ID", "Monthly.Rpt.Prd", "Servicer.Name", "LAST_RT", "LAST_UPB", "Loan.Age", "Months.To.Legal.Mat", 
              "Adj.Month.To.Mat", "Maturity.Date", "MSA", "Delq.Status", "MOD_FLAG", "Zero.Bal.Code", 
              "ZB_DTE", "LPI_DTE", "FCC_DTE","DISP_DT", "FCC_COST", "PP_COST", "AR_COST", "IE_COST", "TAX_COST", "NS_PROCS",
              "CE_PROCS", "RMW_PROCS", "O_PROCS", "NON_INT_UPB", "PRIN_FORG_UPB_FHFA", "REPCH_FLAG", "PRIN_FORG_UPB_OTH", "TRANSFER_FLG"]
Data_P = pd.read_table('D:/1-Intern/Project_1/2018Q1/Performance_2018Q1.txt', 
                       sep = '|', header = None, names = colnames_P,low_memory=False)


# combine two datasets 
df = pd.merge(Data_A, Data_P, on = 'LOAN_ID')


#Subset Loan on  Nov2018 and Dec2018 respectively 
df_Dec2018 = df[df['Monthly.Rpt.Prd']== '12/01/2018']
df_Dec2018

df_Nov2018 = df[df['Monthly.Rpt.Prd']== '11/01/2018']
df_Nov2018 


#Subset the variables that is useful to calculate SMM and CPR
df_1 =df_Nov2018[['LOAN_ID', 'ORIG_RT', 'ORIG_AMT', 'ORIG_TRM','ORIG_DTE',  'Monthly.Rpt.Prd', 'LAST_RT', 'LAST_UPB', 
                  'Loan.Age','Months.To.Legal.Mat', 'Adj.Month.To.Mat', 'Maturity.Date']]


# the loan on Dec2018, we only should know how much the actual loan has been reduced, so the variable of 'LAST_UPB' is enough. 
df_2 =df_Dec2018[['LOAN_ID', 'Monthly.Rpt.Prd',  'LAST_UPB']]
df_2


# merger the loans appears both in Nov and Dec
df_3 = pd.merge(df_1, df_2,on='LOAN_ID', how='left', suffixes = ('_Nov', '_Dec'))
df_3.head


# Define a function to calculate origination monthly payment  
def monthly_payment_Calculation(x, y,z):
    return (x * (y / 1200)* ((1 + (y / 1200))**z)) / (((1+( y/1200))**z) -1)

df_3['montly_payment'] = monthly_payment_Calculation(df_3.loc[:, 'ORIG_AMT_Dec'], df_3.loc[:, 'ORIG_RT_Dec'], df_3.loc[:, 'ORIG_TRM_Dec'])


#Calculate monthly interest should be payed
df_3['interest_payment_Nov']= df_3['LAST_UPB_Nov'] * (df_3['LAST_RT_Nov']/1200)
df_3['interest_payment_Nov']


#Calculate monthly principal should be payed
df_3['Principal_payment_Nov']= df_3['montly_payment']- df_3['interest_payment_Nov']
df_3['Principal_payment_Nov']


# Here is the part that how many amount of loan  has been deducted. 
df_3['Actual_loan_amount_deducted_Nov'] = df_3['LAST_UPB_Nov']- df_3['LAST_UPB_Dec']
df_3['Actual_loan_amount_deducted_Nov']


#creat a column to calculate the total amount loan that has been payed back on Nov 2018
df_3['Actual_payment_Nov'] = df_3['Actual_loan_amount_deducted_Nov']+ df_3['interest_payment_Nov']
df_3['Actual_payment_Nov']


#calculate SMM on Nov2018
Total_Actual_Payment_Nov = df_3['Actual_payment_Nov'].sum()
Total_monthly_Payment_Nov =df_3['montly_payment'].sum()
Total_monthly_UPB_Nov = df_3['LAST_UPB_Nov'].sum()
Total_monthly_principal_Nov = df_3['Principal_payment_Nov'].sum()
SSM = (Total_Actual_Payment_Nov - Total_monthly_Payment_Nov)/ ( Total_monthly_UPB_Nov - Total_monthly_principal_Nov)
SSM 

#calculate CPR on Nov2018
CPR = (1-(1-SSM)**12)
CPR
