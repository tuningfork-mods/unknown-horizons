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

from unittest import mock

from horizons.constants import SETTINGS
from horizons.engine import engine as engine_module
from horizons.engine.settings import detect_display_resolution


class FakeSettings:
	"""Minimal stand-in for horizons.engine.settings.Settings.

	The real Settings needs FIFE's XML serializer, which the test suite
	replaces with a dummy; the resolution logic only needs set/save.
	"""
	def __init__(self):
		self.values = {}
		self.saved = False

	def set(self, module, name, value):
		self.values[(module, name)] = value

	def save(self):
		self.saved = True


def make_fife(first_run=True):
	"""A Fife instance without running __init__ (which needs a display)."""
	fife = engine_module.Fife.__new__(engine_module.Fife)
	fife._setting = FakeSettings()
	fife._first_run = first_run
	fife.engine_settings = FakeEngineSettings()
	fife.log = FakeLog()
	return fife


class FakeEngineSettings:
	"""Records the live engine settings the resolution is applied to."""
	def __init__(self):
		self.width = None
		self.height = None

	def setScreenWidth(self, width):
		self.width = width

	def setScreenHeight(self, height):
		self.height = height


class FakeLog:
	def info(self, *args):
		pass


def test_1568_detect_display_resolution_is_safe():
	"""Detection never raises; it returns None or a sane (width, height)."""
	result = detect_display_resolution()
	assert result is None or (
		isinstance(result, tuple) and len(result) == 2 and
		all(isinstance(v, int) and v > 0 for v in result))


def test_1568_first_run_applies_detected_resolution():
	"""On first run the detected desktop resolution becomes the setting.

	https://github.com/unknown-horizons/unknown-horizons/issues/1568
	"""
	fife = make_fife(first_run=True)
	with mock.patch.object(engine_module, 'detect_display_resolution',
	                       return_value=(1920, 1080)):
		fife.maybe_autodetect_resolution()

	assert fife._setting.values[(SETTINGS.FIFE_MODULE, 'ScreenResolution')] == '1920x1080'
	assert fife._setting.saved
	# the live engine gets the detected size too, so it applies on this
	# very first start instead of only the second one
	assert fife.engine_settings.width == 1920
	assert fife.engine_settings.height == 1080


def test_1568_failed_detection_keeps_default():
	"""If detection is impossible, nothing is stored and the default stays."""
	fife = make_fife(first_run=True)
	with mock.patch.object(engine_module, 'detect_display_resolution',
	                       return_value=None):
		fife.maybe_autodetect_resolution()

	assert (SETTINGS.FIFE_MODULE, 'ScreenResolution') not in fife._setting.values
	assert not fife._setting.saved


def test_1568_subsequent_run_does_not_change_resolution():
	"""On later runs the stored (possibly user-changed) value is kept.

	The issue explicitly requires no redetection once settings exist.
	"""
	fife = make_fife(first_run=False)
	detect = mock.Mock(return_value=(1920, 1080))
	with mock.patch.object(engine_module, 'detect_display_resolution', detect):
		fife.maybe_autodetect_resolution()

	detect.assert_not_called()
	assert (SETTINGS.FIFE_MODULE, 'ScreenResolution') not in fife._setting.values
	assert not fife._setting.saved
