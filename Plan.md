# Plan

## 1. Data preparation
- New features: 
  - <span style="color:orange"> Acceleration (an)
  - <span style="color:green"> duration( events)
  - <span style="color:green"> one hot encoding event, seq or set
  - <span style="color:green"> Alimentation (AC/DC/Battery)

- Filter:
  - Clean:
    - <span style="color:green"> remove doubles,
    - <span style="color:green"> filter window
    - <span style="color:red"> remove outliers (Algerie)
  - Keep only relevant features
    - <span style="color:red"> wrapper (backward, forward)
    - <span style="color:red"> correlation/ mRMR/ PCA
    - <span style="color:red"> use relevence factor (on ev., Al./ev., Acc./ev., Al./Acc., Al./Acc./ev. )
    - <span style="color:red"> F1 score ?
    - <span style="color:red"> add less relevent factors one by one

## 2. Data mining:
- Frequent set / sequence
  - <span style="color:green"> FP-Growth
  - <span style="color:red"> sequence mining
- Location
    - <span style="color:green"> map
- AC/DC/Battery
   - <span style="color:green"> tuple with events -> FP-Growth
- Vehicle :
   - <span style="color:green"> association vehicle <-> accident type

## 3. Model Training
- <span style="color:red"> Random forest
- <span style="color:red"> Any multiclass model

## 4. Verification 
- Accuracy metric
  - <span style="color:red"> crossvalidation
  - <span style="color:red"> confusion matrix
  - <span style="color:red"> accuracy
    
- Feedbackloop:
  - <span style="color:red"> add Feature one by one
  - <span style="color:red"> change module (prep, filter, time window, ...)
