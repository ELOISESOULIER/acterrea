source("lung.rcpp.R")
library(truncnorm)
graphics.off()

T <- 200
dt <- 0.01
tt <- seq(dt, T, by = dt) - dt

simulate <- function(nn, T  = 200, dt = 0.01) {
  ## preliminary
  blocks <- floor(seq(0, T - dt, by = dt)/5)
  ## random component
  taub <- runif(nn, min = 0.7, max = 0.8)
  accident <- rbinom(nn, 1, prob = 1/10)
  print("Number of accident")
  print(sum(accident))
  TBreak <- rep(T, nn)
  Tchar <- rep(T, nn)
  taubBreak <- taub
  wacc <- which(accident == 1)
  lwacc <- length(wacc)
  TBreak[wacc] <- rtruncnorm(lwacc, a = TBreak[wacc]/4, b = 3*TBreak[wacc]/4,
                             mean = TBreak[wacc]/2, sd = TBreak[wacc]/8)
  Tchar[wacc] <- runif(lwacc, min = 10, max = 30)
  taubBreak[wacc] <- runif(lwacc, min = 1, max = 1.5) * taub[wacc]
  ## deterministic component
  out <- lapply(seq.int(1, nn), function(ii) {
    traj <- Sample(T = T, dt = dt,
                   TBreak = TBreak[ii],
                   taub = taub[ii],
                   taubBreak = taubBreak[ii],
                   tchar = Tchar)
    sapply(1:ncol(traj), function(col) {tapply(traj[, col], blocks, mean)})
  })

  return(out)
}

t1 <- system.time(OUT <- simulate(100))

if (FALSE) {
  out <- OUT[[2]]
  par(mfrow = c(3, 1))
  plot(out[, 1], out[, 2], type = "l", xlab = "Vol", ylab = "Flow")
  plot(tt, out[, 3], type = "l", xlab = "time", ylab = "Conc")
  plot(tt, out[, 4], type = "l", xlab = "time", ylab = "O2 Flux")
}

out_O2 = sapply(OUT, function(mat) {mat[, 4]})

matplot(out_O2, type = "l",
        xlab = "time", ylab = "O2 Flux")

save(out_O2, file="out_O2.RData")