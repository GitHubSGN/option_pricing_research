from decimal import Decimal

from pydantic import BaseModel


class Greeks(BaseModel):
    theoretical: Decimal
    delta: Decimal
    gamma: Decimal
    theta: Decimal
    vega: Decimal
    rho: Decimal

    def reverse_greeks(self):
        self.delta = -self.delta
        self.gamma = -self.gamma
        self.theta = -self.theta
        self.vega = -self.vega
        self.rho = -self.rho