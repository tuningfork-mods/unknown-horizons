# ###################################################
# Copyright (C) 2026 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

from horizons.command.building import Build
from horizons.component.storagecomponent import StorageComponent
from horizons.constants import BUILDINGS, RES
from tests.game import game_test, settle


@game_test()
def test_ticket_2741_mine_output_collected(s, p):
	"""
	Mined materials must be picked up from the mine by the settlement's
	storage collectors instead of piling up in the mine.
	https://github.com/unknown-horizons/unknown-horizons/issues/2741
	"""
	settlement, island = settle(s)
	warehouse = settlement.warehouse

	assert Build(BUILDINGS.MOUNTAIN, 30, 35, island, ownerless=True)(None)
	mine = Build(BUILDINGS.MINE, 30, 35, island, settlement=settlement)(p)
	assert mine

	# connect the mine with the warehouse via a road west of both
	# (mine is 5x5 at 30-34,35-39 with loading area on its west edge x=30,y=36-38)
	# road must touch the warehouse (30-32,20-22) orthogonally
	for y in range(21, 39):
		result = Build(BUILDINGS.TRAIL, 29, y, island, settlement=settlement)(p)
		assert result, "road build failed at (29, {})".format(y)

	# let the mine produce some iron ore
	s.run(seconds=60)
	mine_inventory = mine.get_component(StorageComponent).inventory
	assert mine_inventory[RES.IRON_ORE] > 0

	# the storage collectors should now empty the mine into the warehouse
	s.run(seconds=240)
	warehouse_inventory = warehouse.get_component(StorageComponent).inventory
	assert warehouse_inventory[RES.IRON_ORE] > 0, \
		'mine produced {} iron ore, but warehouse received none'.format(mine_inventory[RES.IRON_ORE])
