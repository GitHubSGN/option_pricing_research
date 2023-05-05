import numpy as np
from tools.draw_util import line_plot

def rate_m():
    '''
    compounding rate v.s. interest frequency
    :return:
    '''

    r = 0.025
    n = 40
    m = np.arange(10,310) / 10
    rate = (1+r/m) ** (m*n)

    line_plot(list(m), [list(rate)], legend=None, x_label='interest frequency', y_label='rate',
              figure_name=f'compounding rate v.s. interest frequency when R={r*100}% and n={n}')

if __name__ == '__main__':
    rate_m()