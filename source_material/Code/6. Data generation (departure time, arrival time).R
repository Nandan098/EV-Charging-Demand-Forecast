#######################################################################################################
# 6.  Data generation 
# 6-1. Probability density function profile (arrival and departure time) 
library(patchwork)

ChargingRecords[, StartHour :=hour(StartTime)]
ChargingRecords[, EndHour :=hour(EndTime)]

arrival_time_prob<-ggplot(ChargingRecords, aes(x=StartHour))+
  geom_density(fill="yellow", alpha=0.8)+
  labs(title="Probability Density function profile (arrival time)",x ="Time (1 hour interval)", y = "Probability")



departure_time_prob<-ggplot(ChargingRecords, aes(x=EndHour))+
  geom_density(fill="yellow", alpha=0.8)+
  labs(title="Probability Density function profile (departure time)", x ="Time (1 hour interval)", y = "Probability")


arrival_time_prob + departure_time_prob
ggsave('Figure_7.tiff', width = 10, height = 6, dpi = 330)

# 6-2. Probability density function profile (departure time probability in accordance with arrival time) 
library(ggridges)

ConditionalProbability<-data.frame(matrix(nrow = 23, ncol = 23))
for(i in 0:22){
  bin<-ChargingRecords[StartHour==i]
  for(j in 1:23){
    ConditionalProbability[i,(j-1)]<-nrow(bin[EndHour==j])/nrow(bin)
  }
}


conditional_prob<-ggplot(ChargingRecords, aes(y=as.factor(StartHour), x=EndHour))+
  geom_density_ridges(alpha=0.5)+
  labs(x ="Departure time (1 hour interval)", y = "Arrival time (1 hour interval)")+  
  scale_x_continuous(limits = c(0,23), breaks = seq(0,23,2))
conditional_prob

ggsave('Figure_8.tiff', width = 10, height = 6, dpi = 330)
