
# Adele Gillier et Eloise Soulier

# -- Description --
# - Recuperer les simulations et les acoller en une seule grande trajectoire
# - Ajouter 'new trajec' = 1 si l'on commence une nouvelle trajectoire
# - 'cum mean' est la moyenne cumulée sur une trajectoire. 
#    Au temps t c'est la moyenne des (t-1) valeurs précédentes de la trajectoire
# - Y détermine l'arrivée d'un acciddent par le critère suivant : 
#           |X-cum_mean| > seuil1 OU |X-X0| > seuil2

# install.packages("data.table")

# -- Load data --
load("out_O2.RData")
out_O2 = data.frame(out_O2)

nb_simu = length(out_O2)
nb_t = length(out_O2[['X1']])

# Making the dataset
data = out_O2[[1]]
cummean = cumsum(data) / seq(1, nb_t, 1)
cum_means = c(data[1], cummean[-1])

for (i in 2:nb_simu){
    data_simu = out_O2[[i]]
    data = c(data, data_simu)
    
    # Compute cumulated mean
    cummean = cumsum(data_simu) / seq(1, nb_t, 1)
    cummean = c(data_simu[1], cummean[-1]) # On décale d'un cran pour avoir les moyennes des (t-1) valeurs
    cum_means = c(cum_means, cummean)
}
data = data.frame(data)
colnames(data) = c("X")
data[['cum_mean']] = cum_means

# -- Add the information about beginning a new trajectory --
one_trajec = c(1, rep(0, nb_t - 1))
data[['new_trajec']] = rep(one_trajec, nb_simu)

# -- Accident --
thres_mean = 5e-5
X0 = 0.0042
thres_gal = 0.0004
data = transform(data, Y1 = ifelse(abs(X - cum_mean) > thres_mean , 1, 0))
data = transform(data, Y2 = ifelse(abs(X - X0) > thres_gal , 1, 0))
data = transform(data, Y = ifelse(Y1 + Y2 >= 1 , 1, 0))

# --- ONLINESUPERLEARNER ---
data_train = subset(data, select = c('X', 'Y'))
training_set_size = length(data_train$X)

#data.train <- simulator$simulateWAY(training_set_size + B + 100, qw=llW, ga=llA, Qy=llY, verbose=log)
data.train.static <- OnlineSuperLearner::Data.Static$new(dataset = data)

# Variables
X <- OnlineSuperLearner::RandomVariable$new(formula = X ~ Y_lag_1, family = 'gaussian')
Y <- OnlineSuperLearner::RandomVariable$new(formula = Y ~ X, family = 'binomial')
variable_of_interest <- Y
randomVariables <- c(X, Y)

# Algos
algos <- list()

algos <- append(algos, list(list(algorithm = 'ML.XGBoost',
                       algorithm_params = list(alpha = 0),
                       params = list(nbins = c(6,40), online = TRUE))))

algos <- append(algos, list(list(algorithm = 'condensier::speedglmR6',
                      #algorithm_params = list(),
                      params = list(nbins = c(3,4, 5), online = FALSE))))

# bounds <- OnlineSuperLearner::PreProcessor.generate_bounds(data.train.static)
# pre_processor <- PreProcessor$new(bounds = bounds)

smg_factory <- OnlineSuperLearner::SMGFactory$new()
summaryMeasureGenerator <- smg_factory$fabricate(randomVariables)

log <- FALSE
osl  <- OnlineSuperLearner::OnlineSuperLearner$new(algos, summaryMeasureGenerator = summaryMeasureGenerator,
                                                   verbose = log)


nb_iter = 10
risk <- osl$fit(data.train.static, randomVariables = randomVariables,
                initial_data_size = training_set_size / 2,
                max_iterations = nb_iter,
                mini_batch_size = (training_set_size / 2) / nb_iter)
