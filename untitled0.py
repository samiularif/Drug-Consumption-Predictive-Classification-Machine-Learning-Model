# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16KCHl2C82hP3MLZJl6E1lgdkN_wH9Nmc
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

"""# New Section"""

path = '/content/drive/MyDrive/Colab Notebooks/Drug_Consumption_Quantified.csv'

data = pd.read_csv(path)

data.head(10)

data = data.drop('ID', axis=1)

data.head()

data.isna().sum().sum()

print(f'Orginal shape of data with {data.shape[0]} rows and {data.shape[1]} columns')

data.query("Semer != 'CL0'")

data = data.drop(data[data['Semer'] != 'CL0'].index)

data = data.drop(['Choc','Semer'], axis=1)

data = data.reset_index(drop=True)

data.head()

drugs = ['Alcohol', 'Amyl', 'Amphet', 'Benzos', 'Caff','Cannabis','Coke','Crack',
         'Ecstasy', 'Heroin','Ketamine','Legalh','LSD','Meth','Mushrooms', 'Nicotine','VSA']

def drug_encoder(x):
    if x == 'CL0':
        return 0
    elif x == 'CL1':
        return 1
    elif x == 'CL2':
        return 2
    elif x == 'CL3':
        return 3
    elif x == 'CL4':
        return 4
    elif x == 'CL5':
        return 5
    elif x == 'CL6':
        return 6
    else:
        return 7

for column in drugs:
    data[column] = data[column].apply(drug_encoder)

data.head()

print(data)

corr = data.corr().round(2)
plt.figure(figsize=(20,10))
sns.heatmap(corr, annot= True)

from traitlets.config.application import T
mask = np.zeros_like(corr)
mask[np.triu_indices_from(mask)] = True
plt.figure(figsize=(20,10))
sns.heatmap(corr, annot= True, mask = mask)

low_corr = ['Age', 'Gender', 'Education', 'Alcohol','AScore','Caff']

for column in low_corr:
    data = data.drop(column, axis=1)

data.head()

print(f'In the new dataframe there are {data.shape[0]} rows and {data.shape[1]} columns')

cocaine_df = data.copy()
cocaine_df['coke_user'] = cocaine_df['Coke'].apply(lambda x: 0.5 if x not in [0,1] else 0)
cocaine_df['crack_user'] = cocaine_df['Coke'].apply(lambda x: 0.5 if x not in [0,1] else 0)
cocaine_df['both_user'] = cocaine_df[['coke_user', 'crack_user']].iloc[:].sum(axis=1)
cocaine_df['Cocaine_User'] = cocaine_df['both_user'].apply(lambda x: 1 if x > 0 else 0)
cocaine_df = cocaine_df.drop(['coke_user', 'crack_user', 'both_user' ], axis=1)

meth_df = data.copy()
meth_df['Meth_User'] = meth_df['Meth'].apply(lambda x: 1 if x not in [0,1] else 0)
meth_df = meth_df.drop(['Meth'], axis=1)

heroin_df = data.copy()
heroin_df['Heroin_User'] = heroin_df['Heroin'].apply(lambda x: 1 if x not in [0,1] else 0)
heroin_df = heroin_df.drop(['Heroin'], axis=1)

nic_df = data.copy()
nic_df['Nicotine_User'] = nic_df['Nicotine'].apply(lambda x: 1 if x not in [0,1] else 0)
nic_df = nic_df.drop(['Nicotine'], axis=1)

cocaine_df.head()

meth_df.head()

heroin_df.head()

nic_df.head()

def preprocessing_inputs(df, column):
    df = df.copy()

    # Split df into X and y
    y = df[column]
    X = df.drop(column, axis=1)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

    # Scale X
    scaler = StandardScaler()
    scaler.fit(X_train)

    X_train = pd.DataFrame(scaler.transform(X_train),
                           index=X_train.index,
                           columns=X_train.columns)
    X_test = pd.DataFrame(scaler.transform(X_test),
                          index=X_test.index,
                          columns=X_test.columns)

    return X_train, X_test, y_train, y_test

def plot_confusion_matrix(y,y_predict):
    #Function to easily plot confusion matrix
    cm = confusion_matrix(y, y_predict)
    ax= plt.subplot()
    sns.heatmap(cm, annot=True, ax = ax, fmt='g', cmap='Blues');
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    ax.set_title('Confusion Matrix');
    ax.xaxis.set_ticklabels(['non-user', 'user']); ax.yaxis.set_ticklabels(['non-user', 'user'])

"""Cocaine Model Training"""

X_train, X_test, y_train, y_test = preprocessing_inputs(cocaine_df, 'Cocaine_User')

X_train.head()

print('Train set:', X_train.shape, y_train.shape)
print('Test set:', X_test.shape, y_test.shape)

models = {
            '             Naive Bayes': GaussianNB(),
            '                     Knn': KNeighborsClassifier(),
            '     Logisitc Regression': LogisticRegression(),
            ' Support Vector Machines': SVC(),
            '           Decision Tree': DecisionTreeClassifier()}

for name, model in models.items():
    model.fit(X_train, y_train)
    print (name + ' Trained')

print('                  ACCURACY')
for name, model in models.items():
    yhat = model.predict(X_test)
    acc = accuracy_score(y_test, yhat)

    print(name + ' Accuracy: {:.2%}'.format(acc))
print('---------------------------------------------')
print('                  F1 SCORES')
for name, model in models.items():
    yhat = model.predict(X_test)
    f1 = f1_score(y_test, yhat, pos_label=1)
    print(name + ' F1-Score: {:.5}'.format(f1))

