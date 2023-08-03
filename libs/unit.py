import enum
import random

from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy import Integer, Enum, JSON

from libs.base import Base


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
    equipment = Column(JSON, default=[])
    position = Column(Integer, default=1)
    destroyed = Column(Boolean, default=False)

    def print_full(self) -> str:
        return (f"<Unit(id={self.id}, unit_type={self.unit_type}, amount={self.amount}, "
                f"can_shoot={self.can_shoot}, fight_aggressivity={self.fight_aggressivity}, "
                f"shooting_aggressivity={self.shooting_aggressivity}, fight_armor={self.fight_armor}, "
                f"shooting_armor={self.shooting_armor}, target_range={self.target_range}, "
                f"equipment={self.equipment}, position={self.position}, destroyed={self.destroyed})>")

    def __repr__(self):
        return (f"<Unit(band_id={self.band_id}, id={self.id}, unit_type={self.unit_type}, amount={self.amount}, "
                f"position={self.position})>")

    def move(self, defender):
        print(f"{self} move")
        if defender:
            self.position += 1
        else:
            self.position -= 1

    def target_in_range(self, other_unit: 'Unit') -> bool:
        if other_unit.destroyed:
            return False

        range_limit = 2 if self.can_shoot else 0
        if Equipment.JAVELINS in self.equipment:
            range_limit = 1
        return abs(self.position - other_unit.position) <= range_limit

    def targets_in_range(self, band: 'Band') -> list['Unit']:
        return [unit for unit in band.units if self.target_in_range(unit)]

    def attack(self, other_unit: 'Unit') -> int:
        """This is the main attack function. Simulate fight (and shooting)"""
        num_rolls = self.shooting_aggressivity if self.can_shoot else self.fight_aggressivity
        armor = other_unit.shooting_armor if self.can_shoot else other_unit.fight_armor
        defense_threshold = 4 if self.can_shoot else 5
        successful_hits = 0
        for _ in range(int(num_rolls)):
            score = random.randint(1, 6)
            if Equipment.HEAVY_WEAPON in self.equipment:
                score += 1
            if score >= armor and random.randint(1, 6) >= defense_threshold:
                successful_hits += 1
        return successful_hits

    def suffer_hits(self, successful_hits):
        self.amount = max(0, self.amount - successful_hits)
        if self.amount == 0:
            self.destroyed = True

    def target_factor(self, other_unit: 'Unit') -> float:
        """This function returns a target factor for a given other unit.
        The higher the returned value, the more likely is the unit to be shoot
        """
        weight = sum(equipment_weights[e] for e in self.equipment) * unit_type_weights[self.unit_type]
        target_weight = sum(equipment_weights[e] for e in other_unit.equipment) * unit_type_weights[
            other_unit.unit_type]
        return self.attack(other_unit) * weight * target_weight

    def activation(self, activation_dice_amount: int) -> bool:
        return random.random() <= activate_probability[self.unit_type] * (activation_dice_amount / 8.0)

    # Typical units
    def turn_to_levy(self):
        self.unit_type = UnitType.LEVY
        self.amount = 12
        self.can_shoot = True
        self.fight_aggressivity = 1 / 3.0
        self.shooting_aggressivity = 1 / 2.0
        self.fight_armor = 3
        self.shooting_armor = 3
        self.target_range = 2
        self.equipment = [Equipment.ARCS]
        self.position = 2

    def turn_to_warriors(self):
        self.unit_type = UnitType.WARRIOR
        self.amount = 8
        self.can_shoot = False
        self.fight_aggressivity = 1
        self.shooting_aggressivity = 1 / 2.0
        self.fight_armor = 4
        self.shooting_armor = 4
        self.target_range = 0
        self.position = 1

    def turn_to_guards(self):
        self.unit_type = UnitType.GUARD
        self.amount = 4
        self.can_shoot = False
        self.fight_aggressivity = 2
        self.shooting_aggressivity = 1
        self.fight_armor = 5
        self.shooting_armor = 5
        self.target_range = 0
        self.equipment = [Equipment.HORSES]
        self.position = 4

    def turn_to_lord(self):
        self.unit_type = UnitType.LORD
        self.amount = 1
        self.can_shoot = False
        self.fight_aggressivity = 8
        self.shooting_aggressivity = 4
        # To simulate resistance
        self.fight_armor = 6
        self.shooting_armor = 6
        self.target_range = 0
        self.equipment = [Equipment.HORSES]
        self.position = 4
