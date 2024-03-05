import pandas as pd
from sklearn.model_selection import RepeatedKFold
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
from tqdm import tqdm
import numpy as np
import os

topologies = ['euro28', 'us26']
representation = ['graph_raw_conn', 'graph_raw_mean', 'graph_stat_dg', 'graph_stat_mdg', 'max', 'mean', 'median', 'min', 'std', 'sum', 'var']
# representation = ['graph_stat_mdg']
n_requests = ['100', '125', '150', '175', '200', '225', '250', '275', '300', '325', '350', '375', '400', '425', '450', '475', '500', '525', '550', '575', '600', '625', '650']


results = []

n_components = len(topologies) * len(representation) * len(n_requests) * 4 * 10
p_bar = tqdm(range(n_components), desc='Progress')

for top in topologies:
    for rep in representation:
        for nr in n_requests:
            file_ = f'datasets/{top}/{rep}-{nr}.csv'
            if os.path.exists(file_):
                df = pd.read_csv(file_)
                labels = df.columns[-4:]
                features = df.iloc[:,:-4].values
                # features = df[['density','density']].values

                features[features == np.inf] = 9999999

                for l_name in labels:
                    y = df[l_name].values
                    X = features

                    res_row = {'topology': top, 'representation': rep, 'n_requests': nr, 'label': l_name}
                    
                    rkf = RepeatedKFold(n_splits=2, n_repeats=5)
                    mse_arr = []
                    r2_arr = []
                    for idx, (train_index, test_index) in enumerate(rkf.split(X)):
                        
                        X_train, X_test = X[train_index], X[test_index]
                        y_train, y_test = y[train_index], y[test_index]
                        
                        model = MLPRegressor(max_iter=200)
                        # model = LinearRegression()
                        model.fit(X_train, y_train)
                        y_pred = model.predict(X_test)

                        mse = mean_squared_error(y_test, y_pred)
                        r2 = r2_score(y_test, y_pred)

                        res_row[f'mse_s{idx}'] = mse
                        res_row[f'r2_s{idx}'] = r2
                        p_bar.update(1)
                    
                    results.append(res_row)
                    
            else:
                print(f'File {file_} does not exist')

results_df = pd.DataFrame(results)
print(results_df)

results_df.to_csv('exp_01_results.csv', index=False)




