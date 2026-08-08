from decimal import Decimal
from pydantic import BaseModel,ConfigDict

class PackageOut(BaseModel):
    id: int
    name: str
    price: Decimal
    credit_count: int
    type: str
    model_config = ConfigDict(from_attributes=True)