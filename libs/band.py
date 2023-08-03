import random

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from libs.unit import min_activation_dice

from libs.base import Base
from libs.unit import Unit


class Band(Base):
    __tablename__ = 'bands'

    id = Column(Integer, primary_key=True)
    units = relationship("Unit", backref="band")

    def turn(self, other_band: 'Band'):
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
            if unit.amount >= min_activation_dice[unit.unit_type]:
                activation_dice += 1
        return activation_dice

    def create_typical_band(self, db_session):
        db_session.flush()

        unit = Unit(band_id=self.id)
        unit.turn_to_lord()
        db_session.add(unit)

        unit = Unit(band_id=self.id)
        unit.turn_to_guards()
        db_session.add(unit)

        for i in range(0, 3):
            unit = Unit(band_id=self.id)
            unit.turn_to_warriors()
            db_session.add(unit)

        for i in range(0, 2):
            unit = Unit(band_id=self.id)
            unit.turn_to_levy()
            db_session.add(unit)
