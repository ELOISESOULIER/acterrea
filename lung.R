source("lung.rcpp.R")
graphics.off()

temps <- system.time({
T <- 100
dt <- 0.01
tt <- seq(dt, T, by = dt)
taub = seq(0.75,0.1, by = -.65*dt/100)
OUT <- Sample(T = T, dt = dt, taub = taub)
tt <- head(tt, -1)

par(mfrow = c(3, 1))
plot(OUT[, 1], OUT[, 2], type = "l", xlab = "Vol", ylab = "Flow")
plot(tt, OUT[, 3], type = "l", xlab = "time", ylab = "Conc")
plot(tt, OUT[, 4], type = "l", xlab = "time", ylab = "O2 Flux")
})


## ajouter du bruit sur le signal, transformer un paramètre en vecteur, enregistrer la sortie
