from sqlalchemy.orm import relationship

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from sqlalchemy_utils import database_exists, create_database

from libs.base import Base
from libs.unit import Unit
from libs.unit import min_activation_dice
from sqlalchemy import Column, Boolean, ForeignKey, Integer

import operator

class Band(Base):
    __tablename__ = 'bands'

    id = Column(Integer, primary_key=True)
    units = relationship("Unit", backref="band")
    defender = Column(Boolean, default=False)

    def make_defender(self):
        self.defender = True
        for u in self.units:
            u.position = -u.position
    def band_destroyed(self):
        destroyed = True
        for unit in self.units:
            if not unit.destroyed:
                destroyed = False
                break

        return destroyed

    @staticmethod
    def find_target(current_unit: Unit, other_band: 'Band') -> Unit:
        """Find the best target for the unit"""
        targets = current_unit.targets_in_range(other_band)
        targets = [(current_unit.target_factor(t), t) for t in targets]
        targets.sort(key=operator.itemgetter(0))
        targets.reverse()

        if targets:
            return targets[0][1]
        else:
            return None

    def find_target_and_fight(self, unit, other_band):
        target = self.find_target(unit, other_band)
        if target:
            attack_hits = unit.attack(target)
            print(f"{unit} attack {target}")
            if unit.target_range == 0:
                # This is CAC
                revenge_hits = target.attack(unit)
                unit.suffer_hits(revenge_hits)
            target.suffer_hits(attack_hits)
            print(f"after attack {target}")
        else:
            unit.move(self.defender)

    def turn(self, other_band: 'Band'):
        activation_dice = self.get_activation_dice()

        for unit in self.units:
            if unit.activation(activation_dice):
                self.find_target_and_fight(unit, other_band)
            else:
                print(f"{unit} failed activation")

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


if __name__ == '__main__':
    engine = create_engine('sqlite:///work.db')
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)
    session = Session(engine)

    # Test the turn function
    band1 = Band()
    band2 = Band()
    session.add(band1)
    session.add(band2)

    band1.create_typical_band(session)
    band2.create_typical_band(session)
    band2.make_defender()

    session.commit()

    for i in range(7):
        print(i)
        print()
        band1.turn(band2)
        print()
        band2.turn(band1)
        print()

