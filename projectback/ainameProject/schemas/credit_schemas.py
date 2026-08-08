from pydantic import BaseModel

class CreditBalanceOut(BaseModel):
    balance: int
    logo_balance: int