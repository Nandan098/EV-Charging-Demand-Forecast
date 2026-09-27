#######################################################################################################
# 4.  plotting charging probability profiles (EV user)  

uid<-unique(ChargingRecords$UserID)
UserProfilePlot<-data.frame(matrix(nrow =length(uid) , ncol = 97))

for(i in 1:length(uid)){
  bin<-ChargingRecords[UserID==uid[i]]
  days<-sort(unique(c(bin$StartDay, bin$EndDay)))
  UserProfilePlot[i,1]<-uid[i]
  if(nrow(bin)>1 & nrow(bin)>=(days[length(days)]-days[1])/7){
    for(j in 1:96){
      #    if(nrow(bin)>1){
      #    if(days[length(days)]-days[1]>1){
      #UserProfilePlot[i,(j+1)]<-nrow(bin[(EndDay-StartDay==1 & Start15min<=j)|(EndDay-StartDay==0 & Start15min<=j  & End15min>=j)|(EndDay-StartDay==1 & End15min>=j)])/(days[length(days)]-days[1])
      UserProfilePlot[i,(j+1)]<-nrow(bin[(EndDay-StartDay==1 & Start15min<=j)|(EndDay-StartDay==0 & Start15min<=j  & End15min>=j)|(EndDay-StartDay==1 & End15min>=j)])/(nrow(bin))*100
    }
  }
}
UserProfilePlot<-na.omit(UserProfilePlot)
UserProfilePlot<-UserProfilePlot[-1,]
colnames(UserProfilePlot)<-c("Uid", 1:96)


# EV user segmentation in accordance with charging pattern 
require(NbClust)
set.seed(1234)

UserProfilePlot_k_means_num=NbClust(UserProfilePlot[,2:ncol(UserProfilePlot)],min.nc=2,max.nc=10,method="kmeans")
table(UserProfilePlot_k_means_num$Best.n[1,])

barplot(table(UserProfilePlot_k_means_num$Best.n[1,]),xlab="Number of Clusters",ylab="Number of Criteria",
        main="Number of Clusters Chosen by 10 criteria")



wssplot <- function(data, nc = 10, seed = 1234) {
  wss <- (nrow(data) - 1) * sum(apply(data, 2, var))
  for (i in 2:nc) {
    set.seed(seed)
    wss[i] <- sum(kmeans(data, centers=i)$withinss)}
  plot(1:nc, wss, type="b", xlab = "Number of Clusters",
       ylab = "Within groups sum of squares")}

wssplot(UserProfilePlot[,2:ncol(UserProfilePlot)])

no_cluster<-4
UserProfilePlot_k_means<-kmeans(UserProfilePlot[,2:ncol(UserProfilePlot)], no_cluster)

for(i in 1:no_cluster){
  if(i == 1){
    cluster_result<-as.data.frame(apply(UserProfilePlot[which(UserProfilePlot_k_means$cluster==i),2:ncol(UserProfilePlot)],2, mean))
    cluster_result<-cbind(c(1:96),cluster_result)
    cluster_result<-cbind(i,cluster_result)
    colnames(cluster_result)<-c("Cluster","Time", "Probability")
    
  }else{
    df<-as.data.frame(apply(UserProfilePlot[which(UserProfilePlot_k_means$cluster==i),2:ncol(UserProfilePlot)],2, mean))
    df<-cbind(c(1:96),df)
    df<-cbind(i,df)
    colnames(df)<-c("Cluster", "Time", "Probability")
    cluster_result <-rbind(cluster_result, df)
  }
}
cluster_result$Cluster<-as.factor(cluster_result$Cluster)

# representative charging probability patterns (EV user, the number of clusters: 4)

UserProfile_plot<-ggplot2::ggplot(cluster_result, aes(x = Time, y = Probability, colour = Cluster)) + 
  geom_line() + 
  scale_x_continuous(breaks = c(1, 24, 48, 72 ,96), labels =c("00:15", "06:00", "12:00", "18:00","00:00"))+
  labs(x ="Time (15 minute interval)", y = "Probability (%)")

ggsave('Figure_4.tiff', width = 10, height = 6, dpi = 330)


