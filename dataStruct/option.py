from decimal import Decimal
from pydantic import BaseModel
from typing import (Literal, Optional)


class Option(BaseModel):
    type: Literal['CALL', 'PUT']
    underlying: str
    strike_price: Decimal
    expiration_timestamp: int
    now_timestamp: Optional[int]
    underlying_price: Optional[Decimal]
    interest: Optional[Decimal]
    volatility: Optional[Decimal]
    position: Decimal = Decimal(1)
    contract_size: Decimal = Decimal(1)

    # @staticmethod
    # def parse_req(request: PricingRequest):
    #     if request.volatility == Decimal(0):
    #         request.volatility = cal_volatility(request.underlying)
    #     result = Option.parse_obj(request)
    #     return result

    def pay_off(self, price):
        if self.type=='CALL':
            payoff = max(Decimal(price) - self.strike_price, 0)
        else:
            payoff = max(self.strike_price - Decimal(price), 0)
        payoff *= self.position*self.contract_size
        return payoff

    def is_same_option(self, option):
        if self.type == option.type \
                and self.underlying == option.underlying \
                and self.strike_price == option.strike_price \
                and self.expiration_timestamp == option.expiration_timestamp \
                and self.contract_size == option.contract_size:
            return True
        else:
            return False

