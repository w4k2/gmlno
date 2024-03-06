import pandas as pd
import scipy.stats as stats
from tqdm import tqdm
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()

# analiza statystyczna, tabele
results = pd.read_csv('01_experiment_results.csv')

topologies = ['euro28', 'us26']

representation = [
    'graph_raw_conn',
    'graph_raw_mean',
    'graph_stat_dg',
    'graph_stat_mdg',
    # 'max',
    'mean',
    # 'median',
    # 'min',
    'std',
    'sum',
    # 'var',
]

le.fit(representation)

n_requests = [
    100, 125, 150, 175,
    200, 225, 250, 275,
    300, 325, 350, 375,
    400, 425, 450, 475,
    500, 525, 550, 575,
    600, 625, 650,
]

metrics = [
    'mae',
    'r2',
    'aobt',
]


targets = [
    'avg_transceivers',
    'max_transceivers',
    'sum_slots',
    'avg_max_slot'
]
statistical_significance = {}
mean_data = {}

n_components = len(topologies) * len(n_requests) * len(metrics) * len(targets) * len(representation) * (len(representation) - 1)
p_bar = tqdm(range(n_components), desc='Progress')

for top in topologies:
    for nr in n_requests:
        for metric in metrics:
            for target in targets:
                for rep1 in representation:
                    better = []
                    data1 = results[(results['topology'] == top) & (results['representation'] == rep1) & (results['n_requests'] == nr) & (results['target'] == target)]
                    mask = data1.columns.str.contains(f'{metric}_*')
                    data1 = data1.loc[:, mask].values[0]

                    mean_data[(top, nr, metric, target, rep1)] = (np.mean(data1), np.std(data1))

                    for rep2 in representation:
                        if rep1 == rep2:
                            continue
                        # print(metric)
                        

                        data2 = results[(results['topology'] == top) & (results['representation'] == rep2) & (results['n_requests'] == nr) & (results['target'] == target)]
                        mask = data2.columns.str.contains(f'{metric}_*')
                        data2 = data2.loc[:, mask].values[0]
                        
                        res = stats.ttest_rel(data1, data2)
                        if res.pvalue < 0.05:
                            if 'r2' in metric:
                                if res.statistic > 0:
                                    better.append(rep2)
                            else:
                                if res.statistic < 0:
                                    better.append(rep2)

                        p_bar.update(1)
                    if better:
                        statistical_significance[(top, nr, metric, target, rep1)] = better

pickle.dump(statistical_significance, open('statistical_significance.pkl', 'wb'))
pickle.dump(mean_data, open('mean_data.pkl', 'wb'))

statistical_significance = pickle.load(open('statistical_significance.pkl', 'rb'))
mean_data = pickle.load(open('mean_data.pkl', 'rb'))


# for row in range(len(n_requests)*2):
#     table += 'euro28 & 100 '
#     for rep in representation:
#         table += '& 10+-2 '
    
#     table += ' \\\\ \\hline \n'

for idx, metric in enumerate(metrics):
    for jdx, target in enumerate(targets):

        
        table = '\\begin{table}[h]\n'
        table += f'\\caption{{Metric {metric.upper()} for {target.replace("_", "-")}}}\n'
        
        table += '''
        \\centering
        \\resizebox*{!}{\\linewidth}{%
        \\begin{tabular}{
        '''

        table += 'cc'+'c' * (len(representation)) + '} \\toprule \n'

        table += ' topology & n requests '
        for rep in representation:
            table += f'& {rep.replace("_","-")} '

        table += '\\\\ \\toprule\n '


        for top in topologies:
            for kdx, nr in enumerate(n_requests):
                if nr == 350:
                    table += ' \\multirow{4}{*}{'+top+'}'+' & \multirow{2}{*}{'+str(nr)+'}'
                else:
                    table += ' & \multirow{2}{*}{'+str(nr)+'}'
                    # table += f' & {nr}'
                
                for rep in representation:
                    if (top, nr, metric, target, rep) in statistical_significance.keys():
                        if kdx % 2 == 0:
                            table += f'& \\textit{{ {str(le.transform(statistical_significance[(top, nr, metric, target, rep)]) + 1)[1:-1]} }}'
                        else:
                            table += f'& \cellcolor[HTML]{{EFEFEF}} \\textit{{ {str(le.transform(statistical_significance[(top, nr, metric, target, rep)]) + 1)[1:-1]} }}'
                    else:
                        if kdx % 2 == 0:
                            table += '& '
                        else:
                            table += '& \cellcolor[HTML]{EFEFEF} '

                table += ' \\\\ \n'
                table += ' & ' 
                for rep in representation:
                    if kdx % 2 == 0:
                        table += f'& {mean_data[(top, nr, metric, target, rep)][0]:.2f} $\\pm$ {mean_data[(top, nr, metric, target, rep)][1]:.2f}'
                    else:
                        table += f'& \cellcolor[HTML]{{EFEFEF}} {mean_data[(top, nr, metric, target, rep)][0]:.2f} $\\pm$ {mean_data[(top, nr, metric, target, rep)][1]:.2f}'
                if nr == 650:
                    table += ' \\\\ \\midrule \n'
                else:
                    table += ' \\\\ \n'
                    # table += ' \\\\ \\cline{2-13} \n'

                    

                    # print(f'{top}, {nr}, {metric}, {target}, {rep}: {mean_data[(top, nr, metric, target, rep)]}')

        table += '''
        \\bottomrule
        \\end{tabular}%
        }

        \\end{table}
        '''

        print(table, file=open(f'tables_/table_m{idx}_t{jdx}.tex', 'w'))

    
# print(mean_data)
# print(statistical_significance.keys())

# table = '''
# \\begin{table}[h]
# \\begin{tabular}
# {lllll}
# 1 & 2 & 3 & 4 & 5 \\\\
# 3 & 4 & 5 & 6 & 7 \\\\
# 3 & 2 & 3 & 1 & 4 \\\\
# 6 & 43 & 2 & 1 & 3
# \\end{tabular}
# \\end{table}
# '''



