import QuantLib as ql
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP
from typing import Dict

from dataStruct.greeks import Greeks
from dataStruct.option import Option
from dataStruct.constant import Constant
# from tools.date_util import timestamp_to_symbolstr

import numpy as np
from scipy.stats import norm

def quote_option_sc(option: Option) -> Greeks:
    # calculate price and greeks for option by self-typing formulations
    T = Decimal( (option.expiration_timestamp - option.now_timestamp) / Constant.ONE_YEAR_IN_DAY / Constant.ONE_DAY_IN_MILLI )
    if T==0:
        T=Decimal(0.00001)
    d_denominator = Decimal(option.volatility * np.sqrt(T))
    d1 = Decimal( np.log( float(option.underlying_price / option.strike_price) ) ) + (option.interest + option.volatility ** 2 / Decimal(2)) * T
    d1 = float(d1 / d_denominator)
    d2 = float(d1 - float(d_denominator))
    K_discount = option.strike_price * np.exp(-1 * option.interest * T)

    result = {}
    result['gamma'] = Decimal(norm.pdf(d1)) / option.underlying_price / d_denominator
    result['vega'] = result['gamma'] * option.volatility * option.underlying_price ** 2 * T
    if option.type.lower() == 'call':
        result['delta'] = Decimal(norm.cdf(d1))
        result['theoretical'] = option.underlying_price * result['delta'] - K_discount * Decimal(norm.cdf(d2))
        result['theta'] = option.underlying_price * Decimal(norm.pdf(d1)) * option.volatility ** 2 / d_denominator / 2 + option.interest * K_discount * Decimal(norm.cdf(d2))
        result['rho'] = T * K_discount * Decimal(norm.cdf(d2))
    else:
        result['delta'] = Decimal(norm.cdf(d1)) - 1
        result['theoretical'] = option.underlying_price * result['delta'] + K_discount * Decimal(norm.cdf(-d2))
        result['theta'] = option.underlying_price * Decimal(norm.pdf(d1)) * option.volatility ** 2 / d_denominator / 2 - option.interest * K_discount * Decimal(norm.cdf(-d2))
        result['rho'] = -T * K_discount * Decimal(norm.cdf(-d2))

    result['vega'] = result['vega'] / 100
    result['rho'] = result['rho'] / 100
    result['theta'] = -result['theta'] / Constant.ONE_YEAR_IN_DAY
    days_to_expiration = Decimal(
        option.expiration_timestamp - option.now_timestamp) / Decimal(Constant.DAYS_IN_MILL_DECIMAL)
    if days_to_expiration < 1:
        result['theta'] = result['theta'] * days_to_expiration


    result = Greeks.parse_obj(result)

    return result



def quote_option(option: Option) -> Greeks:
    # calculate price and greeks for option by quantlib
    result = price_and_greeks(option.type, option.strike_price, option.expiration_timestamp, option.now_timestamp,
                              option.underlying_price, option.interest, option.volatility)
    result = Greeks.parse_obj(result)

    return result


def price_and_greeks(instrument_type: str, strike_price: Decimal, expiration_timestamp: int, now_timestamp: int,
                     underlying_price: Decimal, interest: Decimal, volatility: Decimal,
                     contract_size=Decimal('1')) -> Dict:
    now = to_ql_date(now_timestamp)
    ql.Settings.instance().evaluationDate = now
    ql.Settings.instance().includeReferenceDateEvents = True
    option_type = ql.Option.Put
    if instrument_type.lower() == 'call':
        option_type = ql.Option.Call

    # Instrument
    payoff = ql.PlainVanillaPayoff(option_type, float(strike_price))
    european_exercise = ql.EuropeanExercise(to_ql_date(expiration_timestamp))
    euro_option = ql.EuropeanOption(payoff, european_exercise)

    # Price Engine
    initial_value = ql.QuoteHandle(ql.SimpleQuote(float(underlying_price)))
    interest_rate = ql.YieldTermStructureHandle(ql.FlatForward(
        0, ql.NullCalendar(), float(interest), ql.Actual365Fixed()))
    volatility = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(
        now, ql.NullCalendar(), float(volatility), ql.Actual365Fixed()))

    process = ql.BlackScholesProcess(
        initial_value, interest_rate, volatility)

    engine = ql.AnalyticEuropeanEngine(process)

    euro_option.setPricingEngine(engine)

    theta = Decimal(euro_option.thetaPerDay())
    days_to_expiration = Decimal(
        expiration_timestamp - now_timestamp) / Decimal(Constant.DAYS_IN_MILL_DECIMAL)
    if days_to_expiration < 1:
        theta = theta * days_to_expiration

    return {
        'theoretical': (
            Decimal(euro_option.NPV()) * contract_size).quantize(
            Constant.PRICE_PRECISION,
            rounding=ROUND_UP),
        'delta': Decimal(
            euro_option.delta()).quantize(
            Constant.GREEKS_PRECISION,
            rounding=ROUND_HALF_UP),
        'gamma': Decimal(
            euro_option.gamma()).quantize(
            Constant.GREEKS_PRECISION,
            rounding=ROUND_HALF_UP),
        'theta': theta.quantize(
            Constant.GREEKS_PRECISION,
            rounding=ROUND_HALF_UP),
        'vega': Decimal(
            euro_option.vega() /
            100).quantize(
            Constant.GREEKS_PRECISION,
            rounding=ROUND_HALF_UP),
        'rho': Decimal(
            euro_option.rho() /
            100).quantize(
            Constant.GREEKS_PRECISION,
            rounding=ROUND_HALF_UP)
    }

def to_ql_date(milliseconds):
    # milliseconds to ql date
    dt = datetime.fromtimestamp(
        int(milliseconds) / 1000, tz=timezone.utc)
    return ql.Date(
        dt.day,
        dt.month,
        dt.year,
        dt.hour,
        dt.minute,
        dt.second,
        0,
        dt.microsecond)



# def cal_option_symbol(option):
#     # generate option symbol for an option
#     symbol = "-".join([option.underlying,
#                        timestamp_to_symbolstr(option.expiration_timestamp),
#                        str(int(option.strike_price)),
#                        "C" if option.type.lower() == "call" else "P"
#                        ])
#     return symbol

def cal_implied_volatility(option, price, x0 = None):
    # calculate implied volatility for option with price
    class IVOptimizeClass:
        def __init__(self, option, price):
            self.option = option
            self.price = price

        def __call__(self, x):
            self.option.volatility = x
            self.result = quote_option(option=self.option)
            return self.result.theoretical - self.price

        def derivative(self, x):
            # vega
            # self.option.volatility = x
            # self.result = quote_option(option=self.option)
            return self.result.vega * 100

    precision = 1e-15
    x0 = 0.50 if x0 is None else x0   # initial iv = 50%
    xmin = 0    # minimum iv = 0
    xmax = 10   # maximum iv = 1000%
    iv_opt = IVOptimizeClass(option, price)

    iv_solver = ql.Newton()
    iv = iv_solver.solve(iv_opt, precision, x0, xmin, xmax)

    return iv


