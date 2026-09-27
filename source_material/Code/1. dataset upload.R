library(data.table) 
library(ggplot2) 
library(hms) 
library(lubridate) 
library(dplyr)
library(tidyr)
library(skimr)
library(extrafont)
library(stringr)

#######################################################################################################
# 1. Dataset upload (EV charging records) 

ChargingRecords<-data.table::fread("E:/google drive/LEJ/usb/Paper/2023/EV dataset/Data/비식별화/ChargingRecords.csv")
ChargingRecords[,StartDatetime := lubridate::ymd_hms(paste(StartDay, StartTime, sep = " "))]  
ChargingRecords[,EndDatetime := lubridate::ymd_hms(paste(EndDay, EndTime, sep = " "))]  

ChargingRecords[,StartTime := as_hms(StartTime)]  
ChargingRecords[,EndTime := as_hms(EndTime)]  
