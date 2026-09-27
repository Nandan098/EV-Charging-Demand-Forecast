#######################################################################################################
# 5.  EV user statistics
# 5-1. Charging periods

UserChargingPeriods<-data.frame(matrix(nrow =length(uid) , ncol = 2))

for(i in 1:length(uid)){
  bin<-ChargingRecords[UserID==uid[i]]
  days<-sort(unique(c(bin$StartDay, bin$EndDay)))
  UserChargingPeriods[i,1]<-uid[i]
  if(nrow(bin)>1 & nrow(bin)>=(days[length(days)]-days[1])/7){
    UserChargingPeriods[i,2]<-mean(diff(unique(sort(bin$StartDay))))
  }
}

UserChargingPeriods<-na.omit(UserChargingPeriods)
UserChargingPeriods<-UserChargingPeriods[-1,]
colnames(UserChargingPeriods)<-c("Uid", "Periods")


UserChargingPeriodsPlot<-ggplot(UserChargingPeriods, aes(x=Periods)) + 
  geom_histogram(binwidth = 1, color="black", fill="gray")+
  labs(x ="Periods (daily interval)", y = "Count")

UserChargingPeriodsPlot
ggsave('Figure_5.tiff', width = 10, height = 6, dpi = 330)



table(round(UserChargingPeriods$Periods))
# 1   2   3   4   5   6   7   8   9  10  11  12  13  15  21  25 
# 289 240 145 131  91  77  54  38  15  12   5   6   3   1   1   1 

# the EV user rate of average charging periods less than one week
length(which(UserChargingPeriods$Periods<=7))/length(UserChargingPeriods$Periods)*100

# 5-2. Monthly charging demand

ChargingRecords[,Month:=month(StartDay)]
MonthlyDemand <- ChargingRecords[,.(MonthlyDemand=sum(Demand)),.(UserID,Month)]
EVUserMonthlyDemand <- MonthlyDemand[,.(Demand=mean(MonthlyDemand)), UserID]
EVUserMonthlyDemand <- EVUserMonthlyDemand[-1,]

EVUserMonthlyDemandPlot<-ggplot(EVUserMonthlyDemand, aes(x=Demand)) + 
  geom_histogram(binwidth = 10, color="black", fill="gray")+
  labs(x ="Monthly demand (kWh)", y = "Count")

EVUserMonthlyDemandPlot
ggsave('Figure_6.tiff', width = 10, height = 6, dpi = 330)
