from typing import Optional

from pydantic import BaseModel, ConfigDict


class RollAdd(BaseModel):
    length: float
    weight: float
    added_date: str
    removed_date: Optional[str] = None


class Roll(RollAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RollId(BaseModel):
    ok: bool = True
    roll_id: int


class Dict_generator:  # объявленная переменная не видна в цикле, поэтому обновляется через класс
    def __init__(self):
        self.dictionary = {}

    def add_el(self, key: int, el: str):
        self.dictionary[key] = el
