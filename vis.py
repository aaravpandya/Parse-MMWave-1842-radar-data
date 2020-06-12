import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import argparse

parser = argparse.ArgumentParser(description='Visualize the points in time.')
parser.add_argument('-p',"--path", type=str,
                    help='Specify path of csv file.')

args = parser.parse_args()

df = pd.read_csv(args.path)

df = df.drop(['Unnamed: 0'], axis=1)

frame = df['frame'].unique()
x = df['x']
y = df['y']

plt.ion()
animated_plot = plt.plot(x, y, 'ro')[0]
for idx, f in enumerate(frame):
    df_ = df[df['frame']==f]
    # df_ = df_[df['v'] > 0]
    animated_plot.set_xdata(df_['x'])
    animated_plot.set_ydata(df_['y'])
    plt.draw()
    plt.pause(0.001)

