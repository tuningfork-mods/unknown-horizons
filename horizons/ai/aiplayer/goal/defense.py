# ###################################################
# Copyright (C) 2008-2017 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you are welcome to redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
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

from horizons.ai.aiplayer.building import AbstractBuilding
from horizons.ai.aiplayer.goal.settlementgoal import SettlementGoal
from horizons.constants import BUILDINGS


class DefenseGoal(SettlementGoal):
	"""Build wooden towers to defend the settlement once it is established."""

	def get_personality_name(self):
		return 'DefenseGoal'

	@property
	def active(self):
		if not super().active:
			return False
		# one tower per N residences, capped
		residences = self.settlement.count_buildings(BUILDINGS.RESIDENTIAL)
		towers = self.settlement.count_buildings(BUILDINGS.WOODEN_TOWER)
		desired = min(residences // self.personality.residences_per_tower, self.personality.max_towers)
		return towers < desired

	def execute(self):
		result = AbstractBuilding.buildings[BUILDINGS.WOODEN_TOWER].build(self.settlement_manager, None)[0]
		self._log_generic_build_result(result, 'wooden tower')
		return self._translate_build_result(result)
