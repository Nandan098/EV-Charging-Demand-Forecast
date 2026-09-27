#######################################################################################################
# 3.  plotting charging probability profiles (EV charger)  
# 3-1. Charger's charging probability profiles (charger location) 
ChargingRecords[,StartWday:=wday(StartDay)]
ChargingRecords[,EndWday:=wday(EndDay)]


ChargingRecords[,Start15min:=as.numeric(round(StartTime/60/15))]
ChargingRecords[which(ChargingRecords$Start15min==0), which(names(ChargingRecords)=="Start15min")]<-96

ChargingRecords[,End15min:=as.numeric(round(EndTime/60/15))]
ChargingRecords[which(ChargingRecords$End15min==0), which(names(ChargingRecords)=="End15min")]<-96

ChargingProfilePlot_loc<-data.frame(matrix(nrow = 96*length(location), ncol = 3))
colnames(ChargingProfilePlot_loc)<-c("Location","Time", "Probability")

for(i in 1:length(location)){
  bin<-ChargingRecords[Location==location[i]]
  for(k in 1:96){
    
    ChargingProfilePlot_loc[(i-1)*96+k,1]<-location[i]
    ChargingProfilePlot_loc[(i-1)*96+k,2]<-k
    
    ChargingProfilePlot_loc[(i-1)*96+k,3]<-nrow(bin[(EndDay-StartDay==1 & Start15min<=k)|(EndDay-StartDay==0 & Start15min<=k  & End15min>=k)|(EndDay-StartDay==1 & End15min>=k)])/(nrow(bin))*100
    
  }
  
}

location_lab<-c("hotel" = "Hotel", "company" = "Company", "apartment"="Apartment", "resort"="Resort", "public area"="Public area", 
                "public institution"="Public institution", "restaurant"="Restaurant", "accommodation"="Accommodation", "golf"="Golf",
                "sightseeing"="Sightseeing", "market"="Market", "camping"="Camping", "public parking lot"="Public parking lot", "bus garage"="Bus garage")

ChargingProfile_plot<-ggplot2::ggplot(ChargingProfilePlot_loc, aes(x = Time, y = Probability)) + 
  geom_line(color="#000099") + 
  scale_x_continuous(breaks = c(1, 24, 48, 72 ,96), labels =c("00:15", "06:00", "12:00", "18:00","00:00"))+
  facet_wrap(. ~ Location, ncol = 3, scales = "free_y", labeller=labeller(Location=location_lab))+
  labs(x ="Time (15 minute interval)", y = "Probability (%)")

setwd("G:/.shortcut-targets-by-id/1RPyiOZQc7I5DMbrLNDX9990XEpQLt2ZH/연구공유/$$$$ NSD EV Data set $$$/Figure")
ggsave('Figure_2.tiff', width = 10, height = 6, dpi = 330)



# 3-2. Charger's charging probability profiles (charger location, the day of week) 
# 1: Sunday, 2:Monday, 3: Tuesday, 4: Wednesday, 5: Thursday, 6: Friday, 7: Saturday

ChargingProfilePlot_loc_wd<-data.frame(matrix(nrow = 96*length(location)*7, ncol = 4))
colnames(ChargingProfilePlot_loc_wd)<-c("Location","Wday", "Time", "Probability")


for(i in 1:length(location)){
  bin<-ChargingRecords[Location==location[i]]
  for(j in 1:7){
    bin_1<-bin[StartWday==j|EndWday==j]
    
    for(k in 1:96){
      
      ChargingProfilePlot_loc_wd[(i-1)*96*7+(j-1)*96+k,1]<-location[i]
      ChargingProfilePlot_loc_wd[(i-1)*96*7+(j-1)*96+k,2]<-j
      ChargingProfilePlot_loc_wd[(i-1)*96*7+(j-1)*96+k,3]<-k
      
      if(j==1){
        ChargingProfilePlot_loc_wd[(i-1)*96*7+(j-1)*96+k,4]<-nrow(bin_1[(StartWday==j & Start15min<=k & EndWday==(j+1))|(StartWday==j & Start15min<=k & EndWday==j & End15min>=k)|(StartWday==(7) & EndWday==j & End15min>=k)])/(nrow(bin))*100
      }else if(j==7){
        ChargingProfilePlot_loc_wd[(i-1)*96*7+(j-1)*96+k,4]<-nrow(bin_1[(StartWday==j & Start15min<=k & EndWday==(1))|(StartWday==j & Start15min<=k & EndWday==j & End15min>=k)|(StartWday==(j-1) & EndWday==j & End15min>=k)])/(nrow(bin))*100
        
      }else{
        ChargingProfilePlot_loc_wd[(i-1)*96*7+(j-1)*96+k,4]<-nrow(bin_1[(StartWday==j & Start15min<=k & EndWday==(j+1))|(StartWday==j & Start15min<=k & EndWday==j & End15min>=k)|(StartWday==(j-1) & EndWday==j & End15min>=k)])/(nrow(bin))*100
      }
    }
  }
}


ChargingProfilePlot_loc_wd$Wday<-as.factor(ChargingProfilePlot_loc_wd$Wday)
ChargingProfilePlot_loc_wd$Time<-as.numeric(ChargingProfilePlot_loc_wd$Time)

ChargingProfileWD_plot<-ggplot2::ggplot(ChargingProfilePlot_loc_wd, aes(x = Time, y = Probability, colour = Wday)) + 
  geom_line() + 
  facet_wrap(. ~ Location, ncol = 3, scales = "free_y", labeller=labeller(Location=location_lab))+  
  scale_color_discrete(name="Weekday", breaks=c( 1, 2, 3, 4, 5, 6, 7), labels=c( "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"))+
  labs(x ="Time (15 minute interval)", y = "Probability (%)")+  
  scale_x_continuous(breaks = c(1, 24, 48, 72 ,96), labels =c("00:15", "06:00", "12:00", "18:00","00:00"))

setwd("G:/.shortcut-targets-by-id/1RPyiOZQc7I5DMbrLNDX9990XEpQLt2ZH/연구공유/$$$$ NSD EV Data set $$$/Figure")
ggsave('Figure_3.tiff', width = 10, height = 6, dpi = 330)



