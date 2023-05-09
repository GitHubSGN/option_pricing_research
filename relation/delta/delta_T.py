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


def delta_T():
    '''
    Delta v.s. Maturity
    try to change underlying price to test in/at/out-of-the-money
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
    maturity = np.arange(0, 300) / 100
    deltas = []
    legends = []
    for op_type in ['PUT']:
        for multiplier in [0.8, 1, 1.2]:
            op.type = op_type
            op.underlying_price = op.strike_price * Decimal(multiplier)
            delta = []
            for m_days in maturity:
                op.now_timestamp = timestamp_plus_deltaday(d, days=-m_days*365)
                gks = quote_option(op)
                delta.append(gks.delta)
            deltas.append(delta)
            if multiplier == 1:
                in_at_out = 'at'
            elif multiplier < 1:
                in_at_out = 'in' if op_type=='PUT' else 'out'
            else:
                in_at_out = 'in' if op_type == 'CALL' else 'out'
            legends.append( op_type + '_' + in_at_out  )
    line_plot(list(maturity), deltas, legend=legends, x_label='T', y_label='delta',
              figure_name='delta v.s. T')



if __name__ == '__main__':
    delta_T()