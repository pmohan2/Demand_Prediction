library(tidyverse)
library(broom)
library(rpart)
library(glmnet)
library(randomForest)
library(caret)
library(xgboost)
library(Matrix)

# Model performance metrics Function
results <- function(true, predicted, df) {
  SSE <- sum((predicted - true)^2)
  SST <- sum((true - mean(true))^2)
  R_square <- 1 - SSE / SST
  RMSE = sqrt(SSE/nrow(df))
  data.frame(
    RMSE = RMSE,
    Rsquare = R_square
  )
}

# Loading csv data
setwd('M:/Spring_2020/TA/Project')
data = read.csv('Model.csv')
data<- na.omit(data)
data<-data[,-c(6,7,8,9)]
str(data)
data$LocationID=as.factor(data$LocationID)
data$Month=as.factor(data$Month)
data$Hour=as.factor(data$Hour)
hist(data$Demand)

# Splitting data for Modelling
train_idx <- sample(x = 1:nrow(data), size = floor(0.75*nrow(data)))
train_data <- data[train_idx,]
test_data <- data[-train_idx,]

# Linear Regression
train_data = train_data[,c(5,1,2,3,4,6,7,8,9,10)]
lr_model = lm(Demand~., data = train_data)
summary(lr_model)
lr_model.fit <- round(predict(lr_model, test_data))
d <- (lr_model.fit - test_data$Demand) ^ 2
MSE <- sum(d)/length(d)
RMSE <- (MSE) ^ 0.5
results(test_data$Demand, lr_model.fit,test_data)

# Actual vs Predicted plot
plot(lr_model.fit[1:10000], test_data$Demand[1:10000], main= 'Actual vs Predicted', xlab = 'Predcited Demand', ylab = 'Actual Demand')
abline(coef=c(0,1), col='green', lwd = 2)

# Classification and Regression Trees (CART)
cart<-rpart(Demand~.,data = train_data, method = "anova")
summary(cart)
plot(VarImpPlot(cart))
text(cart)
test_cart = test_data[,-c(5)]
predictions_cart = predict(cart, test_cart)
results(test_data$Demand,predictions_cart,test_data)
model <- train(
  Demand ~., data = train_data, method = "rpart",
  trControl = trainControl("cv", number = 10),
  tuneLength = 10
)
plot(model)
model$bestTune
cart_p <- prune(cart, cp = 0.01002759)
predictions_cart_p = predict(cart_p, test_cart)
results(test_data$Demand,predictions_cart_p,test_data)
plot(model$finalModel)
text(model$finalModel, digits = 3)

# Random Forest
rfx <- train_data[, -c(5)]
rfmodel <- randomForest(rfx, train_data$Demand, ntree=50, nodesize =10)
rfpred=predict(rfmodel,test_data)
rfpred=round(rfpred)
sort(importance(rfmodel),decreasing = T)
varImpPlot(rfmodel)
plot(importance(rfmodel))
mean(rfpred == train_data$Demand)
results(test_data$Demand,rfpred,test_data)

# Extreme Gradient Boosting (XG Boost)
dtrain <- train_data[,-c(1)]
train_label <- train_data$Demand
train_matrix <- xgb.DMatrix(data = as.matrix(dtrain), label = train_label)

dtest <- test_data[,-c(1)]
test_label <- test_data$Demand
test_matrix <- xgb.DMatrix(data = as.matrix(dtest), label = test_label)

# Cross Validation for nrounds
xgbcv <- xgb.cv(data = train_matrix, nrounds = 5000, nfold = 5, print_every_n = 10, early_stop_round = 20)
xgbcv.data <- data.frame(xgbcv$evaluation_log)
write_csv(xgbcv.data, 'XGBcvData.csv')

# XGBoost model training
xg <- xgboost(data = train_matrix, label = train_label, nrounds = 1200)
pred <- round(predict(xg_trail, test_matrix))
results(test_data$Demand, pred,test_data)

mat <- xgb.importance(model = xg)
xgb.plot.importance(mat)

