import random
import enum

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import ChoiceType
from libs.base import Base
from sqlalchemy import Integer, Enum, JSON

class UnitType(enum.Enum):
    LORD = "lord"
    GUARD = "guard"
    WARRIOR = "warrior"
    LEVY = "levy"


class Equipment(enum.StrEnum):
    ARCS = "arcs"
    JAVELINS = "javelins"
    HORSES = "horses"
    HEAVY_WEAPON = "heavy_weapon"


equipment_weights = {
    Equipment.ARCS: 1.5,
    Equipment.JAVELINS: 1.2,
    Equipment.HORSES: 1.5,
    Equipment.HEAVY_WEAPON: 1,
}

unit_type_weights = {
    UnitType.LORD: 1.3,
    UnitType.GUARD: 1.5,
    UnitType.WARRIOR: 1.2,
    UnitType.LEVY: 1,
}

activate_probability = {
    UnitType.LEVY: 2 / 6.0,
    UnitType.WARRIOR: 3 / 6.0,
    UnitType.LORD: 1,
    UnitType.GUARD: 1,
}

min_activation_dice = {
    UnitType.LEVY: 6,
    UnitType.WARRIOR: 4,
    UnitType.LORD: 1,
    UnitType.GUARD: 1,
}


class Unit(Base):
    __tablename__ = 'units'

    id = Column(Integer, primary_key=True)
    band_id = Column(Integer, ForeignKey('bands.id'))
    unit_type = Column(Enum(UnitType))
    amount = Column(Integer)
    can_shoot = Column(Boolean, default=False)
    fight_aggressivity = Column(Integer)
    shooting_aggressivity = Column(Integer)
    fight_armor = Column(Integer)
    shooting_armor = Column(Integer)
    target_range = Column(Integer)
    equipment = Column(JSON)
    position = Column(Integer)
    destroyed = Column(Boolean, default=False)

    def target_in_range(self, other_unit: 'Unit') -> bool:
        range_limit = 2 if self.can_shoot else 0
        if Equipment.JAVELINS in self.equipment:
            range_limit = 1
        return self.position - abs(other_unit.position) <= range_limit

    def targets_in_range(self, band: 'Band') -> list['Unit']:
        return [unit for unit in band.units if self.target_in_range(unit)]

    def compare_dice_with_armor(self, other_unit: 'Unit') -> int:
        num_rolls = self.shooting_aggressivity if self.can_shoot else self.fight_aggressivity
        armor = other_unit.shooting_armor if self.can_shoot else other_unit.fight_armor
        defense_threshold = 4 if self.can_shoot else 5
        successful_hits = 0
        for _ in range(num_rolls):
            score = random.randint(1, 6)
            if Equipment.HEAVY_WEAPON in self.equipment:
                score += 1
            if score >= armor and random.randint(1, 6) >= defense_threshold:
                successful_hits += 1
        return successful_hits

    def target_factor(self, other_unit: 'Unit') -> float:
        weight = sum(equipment_weights[e] for e in self.equipment) * unit_type_weights[self.unit_type]
        target_weight = sum(equipment_weights[e] for e in other_unit.equipment) * unit_type_weights[
            other_unit.unit_type]
        return self.compare_dice_with_armor(other_unit) * weight * target_weight

    def activation(self, activation_dice_amount: int) -> bool:
        return random.random() <= activate_probability[self.unit_type] * (activation_dice_amount / 8.0)
