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

from horizons.ai.aiplayer.basicbuilder import BasicBuilder
from horizons.ai.aiplayer.building import AbstractBuilding
from horizons.ai.aiplayer.buildingevaluator import BuildingEvaluator
from horizons.ai.aiplayer.constants import BUILDING_PURPOSE
from horizons.constants import BUILDINGS
from horizons.entities import Entities


class AbstractWoodenTower(AbstractBuilding):
	@classmethod
	def _get_buildability_intersection(cls, settlement_manager, size, terrain_type, need_collector_connection):
		coords_set = super(AbstractWoodenTower, cls)._get_buildability_intersection(
			settlement_manager, size, terrain_type, need_collector_connection)
		# towers must be inside the settlement (near what they defend)
		return coords_set.intersection(settlement_manager.settlement.ground_map)

	@property
	def evaluator_class(self):
		return WoodenTowerEvaluator

	@property
	def producer_building(self):
		""" towers don't produce anything """
		return False

	@classmethod
	def register_buildings(cls):
		cls._available_buildings[BUILDINGS.WOODEN_TOWER] = cls


class WoodenTowerEvaluator(BuildingEvaluator):
	need_collector_connection = False

	@classmethod
	def create(cls, area_builder, x, y, orientation):
		builder = BasicBuilder.create(BUILDINGS.WOODEN_TOWER, (x, y), orientation)
		radius = Entities.buildings[BUILDINGS.WOODEN_TOWER].radius

		# value: how much of the settlement + nearby water the tower covers
		coverage = 0
		for coords in builder.position.get_radius_coordinates(radius):
			if coords in area_builder.settlement.ground_map:
				coverage += 2 # settlement tiles matter most
			elif coords in area_builder.session.world.water:
				coverage += 1 # water coverage lets towers engage ships

		# prefer spots away from other towers to spread the defense
		spread = cls._distance_to_nearest_building(area_builder, builder, BUILDINGS.WOODEN_TOWER)
		spread_value = min(spread, radius * 2) if spread is not None else radius * 2

		personality = area_builder.owner.personality_manager.get('WoodenTowerEvaluator')
		value = coverage + spread_value * personality.spread_importance
		return WoodenTowerEvaluator(area_builder, builder, value)

	@property
	def purpose(self):
		return BUILDING_PURPOSE.WOODEN_TOWER


AbstractWoodenTower.register_buildings()
