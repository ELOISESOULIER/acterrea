source("lung.rcpp.R")
graphics.off()


temps <- system.time({
T <- 100
dt <- 0.01
tt <- seq(dt, T, by = dt)

nb_simu = 10
taub_start_seq = rep(0.75, nb_simu)
taub_dgt_seq = rep(T/2, nb_simu)
taub_end_seq = c(rep(0.75, nb_simu/2), seq(0.75, 0.4, by=-0.35/nb_simu*2))

table_conc = data.frame(matrix(tt, ncol=T/dt, nrow=1))
table_O2 = data.frame(matrix(tt, ncol=T/dt, nrow=1))

for (i in 1:nb_simu){
  
  taub_start <- 0.75  # initial value
  taub_end <- 0.4 # end value
  taub_dgt <- T/2  # degeneration time
  params <- c(T, dt, taub_start_seq[i], taub_end_seq[i], taub_dgt_seq[i])
  names(params) <- c("T", "dt", "taub_start", "taub_end","taub_dgt" )
  
  taub1 <- rep(taub_start, taub_dgt/dt - dt)
  taub2 <- seq(taub_start, taub_end, by = -(taub_start - taub_end)*dt/(T - taub_dgt))
  taub <- c(taub1, taub2)
  noise <- rnorm(T/dt, 0, 0.001)
  
  # Launch simulations
  OUT <- Sample(T = T, dt = dt, taub = taub)
  OUT <- OUT + noise
  
  if (i == 1) {
    params_table = data.frame(t(params))
  }
  else{
    params_table = rbind(params_table, params)
  }
  table_conc = rbind(table_conc, OUT[,3])
  table_O2 = rbind(table_O2, OUT[,4])
}

#tt <- head(tt, -1)

par(mfrow = c(3, 1))
plot(OUT[, 1], OUT[, 2], type = "l", xlab = "Vol", ylab = "Flow")
title( paste(names(params),params,collapse=' '))
plot(tt, OUT[, 3], type = "l", xlab = "time", ylab = "Conc")
plot(tt, OUT[, 4], type = "l", xlab = "time", ylab = "O2 Flux")


})

dev.copy(png,'images/plot.png')
dev.off()

names_out = c("Id","Vol", "Flow", "Conc", "O2 Flux")

save(table_conc, file="data_conc.RData")
save(params_table, file="data_param.RData")
save(table_O2, file="data_O2.RData")

## ajouter du bruit sur le signal, transformer un paramètre en vecteur, enregistrer la sortie
