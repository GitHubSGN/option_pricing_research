#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Project ：option_pricing_research 
@File ：premium_T.py
@Author ：dongzhen
@Date ：2022/10/21 10:54 
'''

from decimal import Decimal

from dataStruct.option import Option
from tools.date_util import date_to_timestamp, timestamp_to_datetime, timestamp_plus_deltaday
from tools.draw_util import line_plot
from tools.option_price import quote_option


def premium_T():
    '''
    Premium v.s. Maturity
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
        underlying_price=Decimal(30125.877),
        interest=Decimal(0),
        volatility=Decimal(0.714)
    )

    maturity = [1, 7, 14, 21, 28, 35]

    # premium = intrinsic_value + time_value
    x = list(range(22000, 28000))
    premiums = [[] for i in range(len(maturity))]
    intrinsic_value = []  # payoff
    m_idx = 0
    for m_days in maturity:
        op.now_timestamp = timestamp_plus_deltaday(d, days=-m_days)
        for s in x:
            op.underlying_price = Decimal(s)
            gks = quote_option(op)
            premiums[m_idx].append(gks.theoretical)
            if m_idx==0:
                intrinsic_value.append(op.pay_off(Decimal(s)))
        m_idx += 1
    premiums.append(intrinsic_value)
    line_plot(x, premiums,
              legend=['T='+str(i) for i in maturity]+['intrinsic_value'],
              x_label='S', y_label='premium')


if __name__ == '__main__':
    premium_T()