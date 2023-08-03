import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.ext.declarative import declarative_base
from libs.band import Band
from libs.unit import Unit

from libs.unit import UnitType
from libs.unit import Equipment
from libs.base import Base

from libs.unit import activate_probability


class TestBattleSimulation(unittest.TestCase):
    def setUp(self):
        # Setup a new database for testing
        self.engine = create_engine('sqlite:///test_units.db')
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)

    def tearDown(self):
        # Drop the testing database after the tests
        self.session.close()
        if database_exists(self.engine.url):
            drop_database(self.engine.url)

    def test_activation(self):
        # Test the activation function
        unit = Unit(unit_type=UnitType.LEVY, amount=12, can_shoot=False,
                    fight_aggressivity=1/3.0, shooting_aggressivity=1/2.0,
                    fight_armor=3, shooting_armor=3, target_range=0,
                    equipment=[], position=0)
        self.session.add(unit)
        self.session.commit()

        amount = 500000
        for activation_dice in range(1, 9):
            print(activation_dice)
            activation_acc = 0
            for i in range(1, amount):
                activation_acc = activation_acc + unit.activation(activation_dice)
            activation_avg = (activation_acc/float(amount))

            self.assertLessEqual(
                activation_avg,
                (activate_probability[UnitType.LEVY]*(activation_dice/8.0))+0.002)

    def test_turns(self):
        # Test the turn function
        band1 = Band()
        band2 = Band()
        self.session.add(band1)
        self.session.add(band2)

        band1.create_typical_band(self.session)
        band2.create_typical_band(self.session)

        self.session.commit()

        for i in range(100):
            band1.turn(band2)

            if band2.band_destroyed():
                break

        for u in band2.units:
            self.assertTrue(u.destroyed)


if __name__ == '__main__':
    unittest.main()
