#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Project ：option_pricing_research 
@File ：delta_T.py
@Author ：dongzhen
@Date ：2022/10/21 11:18 
'''

from decimal import Decimal

import numpy as np

from dataStruct.option import Option
from tools.date_util import date_to_timestamp, timestamp_to_datetime, timestamp_plus_deltaday
from tools.draw_util import line_plot
from tools.option_price import quote_option


def theta_S():
    '''
    Theta v.s. Underlying Price
    try to change maturity to test different T
    try to change option type: Call or Put
    :return:
    '''
    s = date_to_timestamp(2022, 6, 10, 0, 0, 0)
    d = date_to_timestamp(2022, 6, 10, 23, 59, 59)
    print(d)

    op = Option(
        type='CALL',
        underlying='BTC',
        strike_price=Decimal(25000),
        now_timestamp=s,
        expiration_timestamp=d,
        underlying_price=Decimal(24000),
        interest=Decimal(0),
        volatility=Decimal(0.714)
    )

    # delta v.s. T
    strike_multipliers = np.arange(1,1000)/300
    thetas = []
    legends = []

    for op_type in ['CALL']:
        op.type = op_type
        op.now_timestamp = timestamp_plus_deltaday(d, days=-7)
        for vol in [0.5,1,2,4]:
            op.volatility = Decimal(vol)
            theta = []
            for multiplier in strike_multipliers:
                op.underlying_price = op.strike_price * Decimal(multiplier)
                gks = quote_option(op)
                theta.append(gks.theta)
            thetas.append(theta)

            legends.append( op_type + '_vol:%.2f%%'%(float(vol))  )
    line_plot(list(strike_multipliers), thetas, legend=legends, x_label='S/K', y_label='theta',
              figure_name='theta v.s. S/K')

if __name__ == '__main__':
    theta_S()