#######################################################################################################
# 2. Data statistics (EV charging sessions)  
# 2-1. duration
charging_day<-sort(unique(c(ChargingRecords$StartDay,ChargingRecords$EndDay)))
start_day<-charging_day[1]
end_day<-charging_day[length(charging_day)]

# 2-2. the number of EV users
# User ID (non-member/members of other companies): 0
length(unique(ChargingRecords$UserID))  #The number of EV user (2336) + non-members/members of other companies

# 2-3. the number of EV chargers
# EV chargering Chargers (own company): 1 
# Chargers of other EV chargering companies: 0
length(unique(ChargingRecords$ChargerID))  # the number of charger: 2119
length(unique(ChargingRecords[ChargerCompany==1, ChargerID]))  # the number of own EV chargering company: 289
length(unique(ChargingRecords[ChargerCompany==0, ChargerID]))  # the number of other EV chargering companies: 1830
nrow(ChargingRecords[ChargerCompany==1]) # own EV chargering company sessions: 45713
nrow(ChargingRecords[ChargerCompany==0]) # other EV chargering companies sessions: 27143


# 2-4. the EV charger location information r
location<-unique(ChargingRecords$Location) #the number of location types: 14
# the type of location: hotel, company, apartment, resort, public area, public institution, restaurant, accommodation      
#golf, sightseeing, market, camping, public parking lot, bus garage

charger_loc_num<-table(ChargingRecords$Location) #records
#accommodation(187), apartment(14038), bus garage(29), camping(1630), company(7558) 
#golf(1029), hotel(8600), market(3005), public area(14082), public institution(7023) 
#public parking lot(3396), resort(8854), restaurant(2222), sightseeing(1203) 

#the number of EV chargers in accordance with location
cl_num<-data.frame(matrix(nrow = length(location), ncol = 1))
rownames(cl_num)<-location
colnames(cl_num)<-c("number")

for(i in 1:length(location)){
  cl_num[i,1]<-nrow(unique(ChargingRecords[Location==location[i], .(ChargerID)]))
}

# 2-5. the number of EV charging sessions
nrow(ChargingRecords)  # The number of EV charging sessions: 72856
table(ChargingRecords$UserID)[1] #The number of non-members and members of other EV charging companies: 31553(43.3)

