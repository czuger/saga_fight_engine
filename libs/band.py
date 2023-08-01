import random

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from libs.unit import min_activation_dice

from libs.base import Base


class Band(Base):
    __tablename__ = 'bands'

    id = Column(Integer, primary_key=True)
    units = relationship("Unit", backref="band")

    def round(self, other_band: 'Band'):
        activation_dice = self.get_activation_dice()
        for unit in self.units:
            if unit.activation(activation_dice):
                targets = unit.targets_in_range(other_band)
                if targets:
                    target = random.choice(targets)
                    successful_hits = unit.target_factor(target)
                    target.amount = max(0, target.amount - successful_hits)
                    if target.amount == 0:
                        target.destroyed = True

    def get_activation_dice(self) -> int:
        activation_dice = 0
        for unit in self.units:
            if self.amount >= min_activation_dice[unit.unit_type]:
                activation_dice += 1
        return activation_dice
