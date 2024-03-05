import os
import numpy as np
import pandas as pd
from tqdm import tqdm

def prepare_flat_data(dir_, n_sets, n_demands):
    mean_sets_data = []
    # full_sets_data = []
    for idx in tqdm(range(n_sets), desc=f'Loading data {dir_}', total=n_sets):
        mean_data = []
        full_data = []
        for jdx in range(n_demands):
            with open(f'data/{dir_}/request-set-{idx}/demands_{idx}/{jdx}.txt') as file_:
                data = []
                for kdx, line in enumerate(file_.readlines()):
                    if kdx > 3:
                        data.append(line.replace('\n', ''))
            mean_data.append(np.array(data, dtype=float).mean())
        
        mean_sets_data.append(mean_data)
        # full_sets_data.append(full_data)

    mean_sets_data = np.array(mean_sets_data)

    labels_path = f'data/{dir_}/request-set-0/results.csv'
    df_labels = pd.read_csv(labels_path)
    for metric_name in tqdm(df_labels.columns[1:], desc='Merge with labels'):

        labels = {}
        for idx in range(n_sets):

            labels_path = f'data/{dir_}/request-set-{idx}/results.csv'
            df_labels = pd.read_csv(labels_path)
            for jdx, data in df_labels.iterrows():
                key = data.iloc[0]

                value = int(data[metric_name])
                labels[idx, key] = value

                
        if not os.path.exists(f'flat_data/{dir_}'):
            os.makedirs(f'flat_data/{dir_}')
        if not os.path.exists(f'flat_data/{dir_}/{metric_name}'):
            os.makedirs(f'flat_data/{dir_}/{metric_name}')

        for n_req in df_labels['n_requests']:
            # print(n_req)
            all_labels = []
            for idx in range(n_sets):
                all_labels.append(labels[idx, n_req])

            data = mean_sets_data[:,:n_req]

            X = data
            y = np.array(all_labels)

            np.savez(f'flat_data/{dir_}/{metric_name}/{n_req}_requests.npz', X=X, y=y)

if __name__ == '__main__':
    
    dir_ = 'euro28'
    n_sets = 100
    n_demands = 650    
    prepare_flat_data(dir_, n_sets, n_demands)

    dir_ = 'us26'
    n_sets = 100
    n_demands = 650
    prepare_flat_data(dir_, n_sets, n_demands)






