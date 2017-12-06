library(inline)
library(Rcpp)

Sample.Rcpp <- cxxfunction(signature(
  RV = "numeric",
  TLC = "numeric",
  FRC = "numeric",
  ETC0 = "numeric",
  El0 = "numeric",
  Elmax = "numeric",
  Pplmax = "numeric",
  I = "numeric",
  E0 = "numeric",
  R  = "numeric", 
  a0 = "numeric", 
  Pat = "numeric",
  PH2O = "numeric",
  Pb0 = "numeric",
  Vc = "numeric",
  taub = "numeric",
  sigma = "numeric",
  g0 = "numeric",
  C = "numeric",
  finsp = "numeric",
  fexp = "numeric",
  V0 = "numeric",
  G0 = "numeric",
  T = "numeric", 
  dt = "numeric"
), body = "
Rcpp::NumericVector RVRV(RV);
Rcpp::NumericVector TLCTLC(TLC);
Rcpp::NumericVector FRCFRC(FRC);
Rcpp::NumericVector ETC0ETC0(ETC0);
Rcpp::NumericVector El0El0(El0);
Rcpp::NumericVector ElmaxElmax(Elmax);
Rcpp::NumericVector PplmaxPplmax(Pplmax);
Rcpp::NumericVector II(I);
Rcpp::NumericVector E0E0(E0);
Rcpp::NumericVector RR(R);
Rcpp::NumericVector a0a0(a0); 
Rcpp::NumericVector PatPat(Pat);
Rcpp::NumericVector PH2OPH2O(PH2O);
Rcpp::NumericVector Pb0Pb0(Pb0);
Rcpp::NumericVector VcVc(Vc);
Rcpp::NumericVector taubtaub(taub);
//std :: cout << taubtaub << std::endl;
Rcpp::NumericVector sigmasigma(sigma);
Rcpp::NumericVector g0g0(g0);
Rcpp::NumericVector CC(C);
Rcpp::NumericVector finspfinsp(finsp); 
Rcpp::NumericVector fexpfexp(fexp);
Rcpp::NumericVector V0V0(V0); 
Rcpp::NumericVector G0G0(G0);
Rcpp::NumericVector TT(T); 
Rcpp::NumericVector dtdt(dt);

Rcpp::IntegerVector NN(1);
NN = floor(TT[0] / dtdt[0]);
Rcpp::NumericVector tt(NN[0] + 1);
Rcpp::NumericVector pp(NN[0] + 1);
Rcpp::NumericVector fltt(1);


for(int i = 0; i <= NN[0]; i++) {
  tt[i] = i * dtdt[0];
  fltt = floor(tt[i] / 5);
  if (tt[i] / 5 - fltt[0] < 0.35) {
    pp[i] = finspfinsp[0];
  } else {
    pp[i] = fexpfexp[0];
  }
}

Rcpp::NumericVector VV(NN[0] + 1);
Rcpp::NumericVector dVdV(NN[0] + 1);
Rcpp::NumericVector dVO2dVO2(NN[0] + 1);
Rcpp::NumericVector dWdW(NN[0] + 1);
Rcpp::NumericVector gggg(NN[0] + 1);
Rcpp::NumericVector pplppl(NN[0] + 1);
Rcpp::NumericVector ppappa(NN[0] + 1);

Rcpp::NumericMatrix output(NN[0] + 1, 4);

VV[0] = V0V0[0];
dVdV[0] = 0;
dVO2dVO2[0] = 0;
dWdW[0] = 0;
gggg[0] = G0G0[0];

double Ptot;
double lambda;
double c;
double PplmP;
double PaPa;
double sat;
double dVO2;
double VTC0;
int test;

VTC0 = RVRV[0] + 0.5 * (TLCTLC[0] - RVRV[0]) ; 

for(int i = 1; i <= NN[0]; i++) {
  // Elas, begin
  c = 1 / (TLCTLC[0] - FRCFRC[0]) -  1 / (FRCFRC[0] - RVRV[0]);
  lambda = E0E0[0] / (pow(TLCTLC[0] - FRCFRC[0], -2) +  pow(FRCFRC[0] - RVRV[0], -2)); 
  Ptot = lambda * (pow(TLCTLC[0] - VV[i - 1], -1) - pow(VV[i - 1] - RVRV[0], -1) - c);
  // Elas, end
  dVdV[i] = (II[0]  / dtdt[0] * dVdV[i - 1] - Ptot - pp[i]) / (II[0] / dtdt[0] + RR[0]);
  dWdW[i] = -pp[i] * dVdV[i];
  VV[i] = VV[i - 1] + dtdt[0] * dVdV[i];
  // phic, begin
  PplmP = ETC0ETC0[0] * (VV[i] - VTC0) - 10 * pow(VV[i] - RVRV[0] + 0.2, -1) + 10 * pow(VTC0 - RVRV[0] + 0.2, -1);
  // phic, end
  pplppl[i] = pp[i] + PplmP;
  // Elas, begin
  Ptot = lambda * (pow(TLCTLC[0] - VV[i], -1) - pow(VV[i] - RVRV[0], -1) - c);
  // Elas, end
  ppappa[i] = pp[i] + Ptot;
  PaPa = gggg[i - 1] * (PatPat[0] - PH2OPH2O[0]);
  // Hill, begin
  sat = pow(PaPa, 2.5) / (pow(26, 2.5) + pow(PaPa, 2.5));
  sat = sat - pow(Pb0Pb0[0], 2.5) / (pow(26, 2.5) + pow(Pb0Pb0[0], 2.5));
  // Hill, end
  dVO2 = 4 * CC[0]  * sat * VcVc[0]  / taubtaub[i];
  dVO2 = dVO2 * 22.4;
  if (dVdV[i] > 0) {
    test = 1;
  } else {
    test = 0;
  }
  gggg[i] = gggg[i - 1] + dtdt[0] / VV[i] * (dVdV[i] * (g0g0[0] - gggg[i - 1]) * test - dVO2);
  dVO2dVO2[i] = dVO2;
}

output(_, 0) = VV;
output(_, 1) = dVdV;
output(_, 2) = gggg;
output(_, 3) = dVO2dVO2;

return(output);
", plugin = "Rcpp")

Sample <- function(T, dt,
                   RV = 1.2,
                   TLC = 6,
                   FRC = 2.64,
                   ETC0 = 3,
                   El0 = 2,
                   Elmax = 25,
                   Pplmax = 10,
                   I = 0,
                   E0 = 5,
                   R  = 2, 
                   a0 = 0.4, 
                   Pat = 760,
                   PH2O = 47,
                   Pb0 = 40,
                   Vc = 0.07,
                   taub = 0.75,
                   sigma = 1.4e-6,
                   g0 = 0.2,
                   C = 2.2e-3,
                   finsp = -2,
                   fexp = 0,
                   V0 = FRC,
                   G0 = 0.15) {
  OUT <- Sample.Rcpp(RV, TLC, FRC, ETC0, El0, Elmax, Pplmax, I, E0, R, a0, Pat, PH2O, Pb0,
                     Vc, taub, sigma, g0, C, finsp, fexp, V0, G0, T, dt)
  OUT[-1, ]
}

