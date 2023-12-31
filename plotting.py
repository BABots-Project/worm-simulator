import os

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import ast
from collections import Counter
if not os.path.exists("../CSV"):
    csv_dir = "CSV/"
    plot_dir = "plots/"
else:
    csv_dir = "../CSV/"
    plot_dir = "../plots/"
def plot_mean_with_df(file_name: str,x_axes:str,group:str = "Social",zoomed:bool = False):
    sp = pd.read_csv(csv_dir + file_name + '.csv')

    sp['Mean time'] = ((sp['Mean time'] * 10) / 60) / 60
    sp['Standard deviation'] = ((sp['Standard deviation'] * 10) / 60) / 60

    sns.set(style="whitegrid")

    for social, g in sp.groupby(group):
        if social:
            linestyle = '-'
            color = '#4C72B0'
        else:
            linestyle = '-'
            color = '#C44E52'

        plt.plot(g[x_axes], g['Mean time'], linestyle=linestyle, marker='', color=color, dashes=[2, 2])
        plt.fill_between(g[x_axes], g['Mean time'] - g['Standard deviation'], g['Mean time'] + g['Standard deviation'],
                         alpha=0.3,color=color)

    plt.xlabel(x_axes)
    if zoomed:
        plt.xlim(0, 2)
        plt.ylim(1.75,3)
    else:
        plt.ylim(0, None)
        plt.yticks(range(0, int(max(sp['Mean time'])) + 3))
    if x_axes == "Number of spots":
        plt.xticks(sp[x_axes])
    plt.ylabel('time (h)')

    colors = ['#C44E52', '#4C72B0']
    scatter = sns.scatterplot(data=sp, x=x_axes, y='Mean time', hue=group, palette=colors, s=100, zorder=10)
    handles, _ = scatter.get_legend_handles_labels()

    custom_legend = plt.legend(handles=handles, labels=['N2 - Solitary agent', 'npr-1 - Social agent'], loc='best')

    for handle in custom_legend.legendHandles:
        handle.set_alpha(1)

    if zoomed:
        plt.savefig(plot_dir + file_name + "_zoomed.png")
    else:
        plt.savefig(plot_dir + file_name + ".png")
    plt.show()


def plot_frequencies(file_name: str, legend):
    sns.set(style="whitegrid")
    data = pd.read_csv(csv_dir + file_name + '_frequencies.csv')
    data['Sense Frequency'] = data['Sense Frequency'].apply(ast.literal_eval)
    data['Food consumption'] = data['Food consumption'].apply(ast.literal_eval)

    if legend == "Gamma":
        data = data[data['Gamma'].isin([0, 1, 2, 3])]

    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    for i, social_value in enumerate([True, False]):
        df = data[data['Social'] == social_value]

        p_sense = []
        p_food = []
        for array in df['Sense Frequency']:
            '''
            total_values = len(array)
            value_counts = Counter(array)
            relative_frequencies = {value: count / total_values for value, count in value_counts.items()}
            values = list(relative_frequencies.keys())
            frequencies = list(relative_frequencies.values())

            data_list = []
            for val, freq in zip(values, frequencies):
                data_list.extend([val] * int(freq * len(values)))
            sns.histplot(data=data_list,ax=axes[0, i],fill=False)
'''
            p_sense.append(array)
        for array in df['Food consumption']:
            p_food.append(array)

        sns.kdeplot(data=p_sense, ax=axes[0, i], legend=False, palette="magma", fill=True)
        sns.kdeplot(data=p_food, ax=axes[1, i],legend=False,palette="magma",fill=True)

        axes[0, i].set_xlim(0, 1)
        axes[0, i].set_xlabel('Individual foraging efficiency')
        axes[0, i].set_ylabel('KDE')
        axes[0, i].set_title('Social - nrp-1' if social_value else 'Solitary - N2')


        axes[1, i].set_xlim(0, 800)
        axes[1, i].set_xlabel('Individual food consumption')
        axes[1, i].set_ylabel('KDE')

    label = data[data['Social'] == True]
    axes[0, 0].legend(legend + " = " + label[legend].astype(str), loc=9)

    plt.tight_layout()
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    plt.savefig(plot_dir + file_name + "_frequencies.png")
    plt.show()

plot_frequencies("10gen_1_minimal_food_clustering","Gamma")