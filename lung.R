source("lung.rcpp.R")
graphics.off()

temps <- system.time({
T <- 100
dt <- 0.01
taub_start <- 0.75 #initial value
taub_end <- 0.4 #end value
taub_dgt <- T/2 #degeneration time
params <- c(T,dt,taub_start,taub_end,taub_dgt)
names(params) <- c("T", "dt", "taub_start", "taub_end","taub_dgt" )

tt <- seq(dt, T, by = dt)
taub <- seq(0.75,0.1, by = -.65*dt/T)
noise <- rnorm(T/dt, 0,0.001)

OUT <- Sample(T = T, dt = dt, taub = taub)
OUT <- OUT + noise
tt <- head(tt, -1)

par(mfrow = c(3, 1))
plot(OUT[, 1], OUT[, 2], type = "l", xlab = "Vol", ylab = "Flow")
title( paste(names(params),params,collapse=' '))
plot(tt, OUT[, 3], type = "l", xlab = "time", ylab = "Conc")
plot(tt, OUT[, 4], type = "l", xlab = "time", ylab = "O2 Flux")


})

dev.copy(png,'plot.png')
dev.off()


## ajouter du bruit sur le signal, transformer un paramètre en vecteur, enregistrer la sortie
