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

        for activation_dice in range(1, 8):
            print(activation_dice)
            activation_acc = 0
            for i in range(1, 1000):
                activation_acc = activation_acc + unit.activation(activation_dice)
            activation_avg = (activation_acc/1000.0)

            self.assertLessEqual(activation_avg, (activation_dice/8.0)*(2/6.0))

    def test_round(self):
        # Test the round function
        band1 = Band()
        band2 = Band()
        unit1 = Unit(unit_type=UnitType.LORD, amount=10, can_shoot=False,
                     fight_aggressivity=3, shooting_aggressivity=0,
                     fight_armor=5, shooting_armor=0, target_range=1,
                     equipment=[Equipment.HEAVY_WEAPON], position=0, band=band1)
        unit2 = Unit(unit_type=UnitType.LEVY, amount=10, can_shoot=False,
                     fight_aggressivity=3, shooting_aggressivity=0,
                     fight_armor=5, shooting_armor=0, target_range=1,
                     equipment=[Equipment.HEAVY_WEAPON], position=1, band=band2)
        self.session.add(band1)
        self.session.add(band2)
        self.session.commit()
        band1.round(band2)
        self.assertTrue(unit2.amount < 10 or unit2.destroyed)


if __name__ == '__main__':
    unittest.main()
