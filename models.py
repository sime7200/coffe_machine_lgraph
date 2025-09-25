from pydantic import BaseModel, field_validator
from typing import List, Optional

class OrderModel(BaseModel):
    action: str = "make_drink" 
    drink: str
    size: str
    sugar: str
    temperature: str
    extras: List[str] = []
    user_id: Optional[str] = None

    @field_validator("size", mode='before')
    def normalize_size(cls, v):
        mapping = {
            "small": "piccolo",
            "medium": "medio",
            "large": "grande",
            "piccolo": "piccolo",
            "medio": "medio",
            "grande": "grande"
        }
        return mapping.get(v.lower(), v)

    @field_validator("sugar", mode='before')
    def normalize_sugar(cls, v):
        mapping = {
            "yes": "sì",
            "yes": "si",
            "si": "sì",
            "sì": "sì",
            "no": "no"
        }
        return mapping.get(v.lower(), v)

    @field_validator("temperature", mode='before')
    def normalize_temperature(cls, v):
        mapping = {
            "cold": "basso",
            "medium": "medio",
            "high": "caldo",
            "basso": "basso",
            "medio": "medio",
            "caldo": "caldo"
        }
        return mapping.get(v.lower(), v)


    @field_validator('sugar', mode='before')
    def normalize_sugar(cls, v):
        if v is None:
            return 'no'
        s = str(v).strip().lower()
        return 'sì' if s in ('sì','si','yes','y') else 'no'
