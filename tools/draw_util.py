import os

from matplotlib import pyplot as plt


def line_plot(x, y, figure_name = 'line', file_name = 'line.png', legend=None,
              x_label='x', y_label='y'):
    # plot mean variance figure
    if legend is None:
        legend = list(range(len(y)))
    plt.title(figure_name)
    for cy in y:
        plt.plot(x, cy, '--')
    plt.legend(legend)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.savefig(file_name)
    plt.show()
