
library(quantreg)
library(dplyr)
library(ggplot2)
library(tidyverse)


#define a workstation
#C:\Workstation\
workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Analysis\\Figures\\'

#give the file path of the dataset prepared
csvfile=paste(workstation,'NormalizedRadimatrix.csv',sep='')

#read the csv file and get the dataframe
DataFrame <- read_csv(csvfile)

head(DataFrame)


#begin to plot
#Sigma
# p_Figure_Combed<-ggplot() +
#   geom_point(data =DataFrame, aes(x = EachIncidenceAngle, y =HH_Sigma ),
#              shape = 3,color = '#999999',size = 2,alpha = .5,stroke=1.1) +
#   stat_smooth(data =DataFrame, aes(x = EachIncidenceAngle, y =HH_Sigma ),
#               size = 0.5,alpha = .5,method = 'lm')+
#   geom_point(data =DataFrame, aes(x = EachIncidenceAngle, y =HV_Sigma ),
#              shape = 16,color = '#fe7217',size = 2,alpha = .5,stroke=1.1) +
#   stat_smooth(data =DataFrame, aes(x = EachIncidenceAngle, y =HV_Sigma ),
#               size = 0.5,alpha = .5,method = 'lm')+
#   geom_point(data =DataFrame, aes(x = EachIncidenceAngle, y =VV_Sigma ),
#              shape = 17,color = '#1379c6',size = 2,alpha = .5,stroke=1.1) +
#   stat_smooth(data =DataFrame, aes(x = EachIncidenceAngle, y =VV_Sigma ),
#               size = 0.5,alpha = .5,method = 'lm')+
#   scale_x_continuous(name = "Incidence angle [degrees]",
#                   limits = c(20, 65), 
#                   breaks = seq(20, 65, by = 10))+
#   scale_y_continuous(name = "",
#                      limits = c(-14, -2), 
#                      breaks = seq(-14, -2, by = 2))+
#   #set some background color, font size, and ticks 
#   theme_linedraw(base_size = 22)+
#   theme(
#     #panel.background = element_rect(fill = "white", colour = "grey50")
#     panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
#     #panel.grid.major.x = element_line(colour = c("white"), size = c(0.33, 0.2)),
#     # axis.text.x = element_text(colour = c(NA,"black")),
#     axis.text.y.right=element_text(angle=90, hjust=0.5),
#     axis.title.y.right = element_text(angle = 90)
#   )
p_Figure_Sigma_Combed<-ggplot() +
  geom_point(data =DataFrame, aes(x = EachIncidenceAngle, y =HH_Sigma ),
             shape = 3,color = '#555555',size = 3,alpha = .6,stroke=1.1) +
  stat_smooth(data =DataFrame, aes(x = EachIncidenceAngle, y =HH_Sigma ),
              color = '#999999',size = 0.5,alpha = .4,method = 'lm')+
  geom_point(data =DataFrame, aes(x = EachIncidenceAngle, y =HV_Sigma ),
             shape = 16,color = '#fe7217',size = 3,alpha = .6,stroke=1.1) +
  stat_smooth(data =DataFrame, aes(x = EachIncidenceAngle, y =HV_Sigma ),
              color = '#ff5217',size = 0.5,alpha = .4,method = 'lm')+
  geom_point(data =DataFrame, aes(x = EachIncidenceAngle, y =VV_Sigma ),
             shape = 17,color = '#1379c6',size = 3,alpha = .6,stroke=1.1) +
  stat_smooth(data =DataFrame, aes(x = EachIncidenceAngle, y =VV_Sigma ),
              color = '#1379c6',size = 0.5,alpha = .4,method = 'lm')+
  #geom_text(data=slopedat,aes(x=2005,y=y,label=paste0("slope = ",slope))) +
  scale_x_continuous(name = "Incidence angle [degrees]",
                     limits = c(20, 70), 
                     breaks = seq(20, 70, by = 10))+
  scale_y_continuous(name = expression(sigma[0]*" [dB]"),
                     limits = c(-14, -2), 
                     breaks = seq(-14, -2, by = 2))+
  #set some background color, font size, and ticks 
  theme_linedraw(base_size = 22)+
  theme(
    #panel.background = element_rect(fill = "white", colour = "grey50")
    panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
    #panel.grid.major.x = element_line(colour = c("white"), size = c(0.33, 0.2)),
    # axis.text.x = element_text(colour = c(NA,"black")),
    axis.text.y.right=element_text(angle=90, hjust=0.5),
    axis.title.y.right = element_text(angle = 90)
  )
p_Figure_Sigma_Combed

#save the figure
ggsave(paste(workstation,"p_Figure_Sigma_Combed_rerun.pdf",sep=''), 
       plot = p_Figure_Sigma_Combed, device='pdf',height = 6, width = 11, units = "in",dpi =500)


#Gamma
p_Figure_Gamma_Combed<-ggplot() +
  geom_point(data =DataFrame, aes(x = EachIncidenceAngle, y =HH_Gamma ),
             shape = 3,color = '#555555',size = 3,alpha = .6,stroke=1.1) +
  stat_smooth(data =DataFrame, aes(x = EachIncidenceAngle, y =HH_Gamma ),
              color = '#999999',size = 0.5,alpha = .4,method = 'lm')+
  geom_point(data =DataFrame, aes(x = EachIncidenceAngle, y =HV_Gamma ),
             shape = 16,color = '#fe7217',size = 3,alpha = .6,stroke=1.1) +
  stat_smooth(data =DataFrame, aes(x = EachIncidenceAngle, y =HV_Gamma ),
              color = '#ff5217',size = 0.5,alpha = .4,method = 'lm')+
  geom_point(data =DataFrame, aes(x = EachIncidenceAngle, y =VV_Gamma ),
             shape = 17,color = '#1379c6',size = 3,alpha = .6,stroke=1.1) +
  stat_smooth(data =DataFrame, aes(x = EachIncidenceAngle, y =VV_Gamma ),
              color = '#1379c6',size = 0.5,alpha = .4,method = 'lm')+
  scale_x_continuous(name = "Incidence angle [degrees]",
                     limits = c(20, 70), 
                     breaks = seq(20, 70, by = 10))+
  scale_y_continuous(name = expression(gamma[0]*" [dB]"),
                     limits = c(-14, -2), 
                     breaks = seq(-14, -2, by = 2))+
  
  #set some background color, font size, and ticks 
  theme_linedraw(base_size = 22)+
  theme(
    legend.position="top",
    #panel.background = element_rect(fill = "white", colour = "grey50")
    panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
    #panel.grid.major.x = element_line(colour = c("white"), size = c(0.33, 0.2)),
    # axis.text.x = element_text(colour = c(NA,"black")),
    axis.text.y.right=element_text(angle=90, hjust=0.5),
    axis.title.y.right = element_text(angle = 90)

  )
p_Figure_Gamma_Combed


#save the figure
ggsave(paste(workstation,"p_Figure_Gamma_Combed_rerun.pdf",sep=''), 
       plot = p_Figure_Gamma_Combed, device='pdf',height = 6, width = 11, units = "in",dpi =500)




#################33
###trash
#shape = 3,color = '#555555',size = 3,alpha = .6,stroke=1.1
df <- mtcars[, c("mpg", "cyl", "wt")]
df$cyl <- as.factor(df$cyl)
head(df)

p_Figure_Legend=ggplot(df, aes(x=wt, y=mpg, group=cyl)) +
  geom_point(aes(shape=cyl, color=cyl),alpha = .7,stroke=1.1)+

  scale_shape_manual(values=c(3, 16, 17))+
  scale_color_manual(labels = c("HH", "HV", "VV"),values=c('#444444','#fe7217', '#1379c6'))+
  scale_size_manual(values=c(4,4,4))+
  theme_linedraw(base_size = 22)
p_Figure_Legend

ggsave(paste(workstation,"p_Figure_Legend.pdf",sep=''), 
       plot = p_Figure_Legend, device='pdf',height = 6, width = 11, units = "in",dpi =500)


