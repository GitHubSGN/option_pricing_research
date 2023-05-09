from decimal import Decimal

from dataStruct.option import Option
from tools.date_util import date_to_timestamp, timestamp_to_datetime
from tools.draw_util import line_plot
from tools.option_price import quote_option


def gamma_S():
    # s = 1654838204192
    # print(timestamp_to_datetime(s))
    s = date_to_timestamp(2022, 6, 3, 0, 0, 0)
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

    # premium = intrinsic_value + time_value
    x = list(range(12000, 38000))
    gamma = []
    for s in x:
        op.underlying_price = Decimal(s)
        gks = quote_option(op)
        gamma.append(gks.gamma)

    line_plot(x,[gamma],
              figure_name="gamma v.s. S",
              legend = ['gamma'],
              x_label='S', y_label='gamma')


if __name__ == '__main__':
    gamma_S()