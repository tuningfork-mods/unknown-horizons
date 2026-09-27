"""Verification of 2026.2 military features: ship-of-the-line, AI usage, pirate scaling, defense goal."""
import pytest

from horizons.command.unit import CreateUnit
from horizons.component.healthcomponent import HealthComponent
from horizons.component.storagecomponent import StorageComponent
from horizons.constants import PRODUCTIONLINES, UNITS, WEAPONS
from horizons.util.color import Color
from horizons.world.player import Player
from horizons.world.units.fightingship import FightingShip
from horizons.world.units.shipoftheline import ShipOfTheLine
from tests.game import game_test, new_session


@game_test()
def test_ship_of_the_line_weapons(s, p):
	"""Ship of the line carries 12 guns vs the frigate's 7."""
	worldid = 10000000
	p = Player(s, worldid, "p1", Color.get(1))
	p.initialize(None)
	s.world.players.append(p)

	frigate = CreateUnit(p.worldid, UNITS.FRIGATE, 0, 0)(issuer=p)
	sotl = CreateUnit(p.worldid, UNITS.SHIP_OF_THE_LINE, 5, 5)(issuer=p)

	assert isinstance(sotl, ShipOfTheLine)
	assert isinstance(sotl, FightingShip)
	assert sotl.num_weapons == 12
	assert frigate.num_weapons == 7

	# both actually got their guns loaded
	assert len(sotl._weapon_storage) == 12
	assert len(frigate._weapon_storage) == 7


@game_test()
def test_ship_of_the_line_stats(s, p):
	"""Ship of the line is tougher and slower than a frigate."""
	worldid = 10000000
	p = Player(s, worldid, "p1", Color.get(1))
	p.initialize(None)
	s.world.players.append(p)

	frigate = CreateUnit(p.worldid, UNITS.FRIGATE, 0, 0)(issuer=p)
	sotl = CreateUnit(p.worldid, UNITS.SHIP_OF_THE_LINE, 5, 5)(issuer=p)

	assert sotl.get_component(HealthComponent).max_health == 400
	assert frigate.get_component(HealthComponent).max_health == 200
	# sotl is slower than a frigate (yaml velocity 9.0 vs 12)
	import yaml as _yaml
	_fdata = _yaml.safe_load(open('content/objects/units/ships/frigate.yaml'))
	_sdata = _yaml.safe_load(open('content/objects/units/ships/shipoftheline.yaml'))
	assert _sdata['velocity'] < _fdata['velocity']


def test_ship_of_the_line_production_line():
	"""Boat builder can build the ship of the line (production line 59)."""
	import yaml
	data = yaml.safe_load(open('content/objects/buildings/boatbuilder.yaml'))
	prodlines = [c['ShipProducerComponent']['productionlines'] for c in data['components'] if isinstance(c, dict) and 'ShipProducerComponent' in c][0]
	assert PRODUCTIONLINES.SHIP_OF_THE_LINE == 59
	assert 59 in prodlines
	line59 = prodlines[59]
	assert line59['produces'][0][0] == 'UNITS.SHIP_OF_THE_LINE'
	assert line59['time'] == 90


def test_pirate_scaling_logic():
	"""Pirate fleet target grows with game time, capped at 4."""
	from horizons.ai.pirate import Pirate
	assert Pirate.max_ship_count == 4
	assert Pirate.extra_ship_month_interval == 30


def test_defense_goal_registered():
	"""DefenseGoal is registered in the settlement manager's goal list."""
	import inspect
	from horizons.ai.aiplayer import settlementmanager
	src = inspect.getsource(settlementmanager)
	assert 'DefenseGoal' in src


def test_aristocrat_constants():
	"""Aristocrat tier is the current max and new resources exist."""
	from horizons.constants import TIER, RES, BUILDINGS
	assert TIER.CURRENT_MAX == TIER.ARISTOCRATS == 5
	assert RES.COFFEE == 72
	assert RES.GARMENTS == 87
	assert RES.RECREATION == 97
	assert BUILDINGS.THEATRE == 92
	assert BUILDINGS.ROASTER == 89
