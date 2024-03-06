import pandas as pd
import scipy.stats as stats
from tqdm import tqdm
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()

# analiza statystyczna, tabele
results = pd.read_csv('04_graph_results.csv')

topologies = ['euro28', 'us26']

representation = [
    'graph_raw_conn',
    'graph_raw_mean',
    'graph_stat_dg',
    'graph_stat_mdg',
]

le.fit(representation)

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

n_components = len(topologies) * len(metrics) * len(targets) * len(representation) * (len(representation) - 1)
p_bar = tqdm(range(n_components), desc='Progress')

for top in topologies:
    for metric in metrics:
        for target in targets:
            for rep1 in representation:
                better = []
                data1 = results[(results['topology'] == top) & (results['representation'] == rep1) & (results['target'] == target)]
                mask = data1.columns.str.contains(f'{metric}_*')
                data1 = data1.loc[:, mask].values[0]

                mean_data[(top, metric, target, rep1)] = (np.mean(data1), np.std(data1))

                for rep2 in representation:
                    if rep1 == rep2:
                        continue
                    # print(metric)
                    

                    data2 = results[(results['topology'] == top) & (results['representation'] == rep2) & (results['target'] == target)]
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
                    statistical_significance[(top, metric, target, rep1)] = better

pickle.dump(statistical_significance, open('g_statistical_significance.pkl', 'wb'))
pickle.dump(mean_data, open('mean_data.pkl', 'wb'))

statistical_significance = pickle.load(open('g_statistical_significance.pkl', 'rb'))
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
        \\begin{tabular}{
        '''

        table += 'c'+'c' * (len(representation)) + '} \\toprule \n'

        table += ' topology'
        for rep in representation:
            table += f'& {rep.replace("_","-")} '

        table += '\\\\ \\toprule\n '


        for top in topologies:
    
            for rep in representation:
                if (top, metric, target, rep) in statistical_significance.keys():
                    table += f'& \cellcolor[HTML]{{EFEFEF}} \\textit{{ {str(le.transform(statistical_significance[(top, metric, target, rep)]) + 1)[1:-1]} }}'
                else:
                    table += '& \cellcolor[HTML]{EFEFEF} '

            table += ' \\\\ \n'

            table += ' {'+top+'}'
            # table += ' & '

            for rep in representation:
                table += f'& \cellcolor[HTML]{{EFEFEF}} {mean_data[(top, metric, target, rep)][0]:.2f} $\\pm$ {mean_data[(top, metric, target, rep)][1]:.2f}'

            table += ' \\\\ \n'


        table += '''
        \\bottomrule
        \\end{tabular}%

        \\end{table}
        '''

        print(table, file=open(f'tables_/g_table_m{idx}_t{jdx}.tex', 'w'))

    
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



