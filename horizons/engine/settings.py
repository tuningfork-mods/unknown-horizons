# ###################################################
# Copyright (C) 2013-2017 The Unknown Horizons Team
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

from fife.extensions.serializers.simplexml import SimpleXMLSerializer

from horizons.constants import LANGUAGENAMES, SETTINGS
from horizons.i18n import change_language


class Settings:

	# Settings key storing the SettingsVersion used to upgrade settings
	SETTINGS_VERSION = "SettingsVersion"

	def __init__(self, settings_file, settings_template_file):
		self._module_settings = {}
		self._module_settings_template = {}
		self._settings_file = settings_file
		self._settings_template_file = settings_template_file
		self._settings_serializer = SimpleXMLSerializer()
		self._settings_serializer.load(settings_file)
		self._settings_template_serializer = SimpleXMLSerializer()
		self._settings_template_serializer.load(settings_template_file)
		if not hasattr(self._settings_template_serializer, 'getModuleName'):
			# Renamed after 0.3.5: https://github.com/fifengine/fifengine/issues/819.
			new_api = self._settings_template_serializer.getModuleNameList
			self._settings_template_serializer.getModuleName = new_api
		self.upgrade_settings()

	def get(self, module, name, default=None):
		if default is None:
			default = self._settings_template_serializer.get(module, name)

		v = self._settings_serializer.get(module, name, default)
		getter = getattr(self, 'get_' + module + '_' + name, None)
		if getter:
			return getter(v)
		else:
			return v

	def set(self, module, name, value):
		setter = getattr(self, 'set_' + module + '_' + name, None)
		if setter:
			value = setter(value)

		# This is necessary, as empty fields return None, but saving
		# None will result in the String 'None' being stored
		if value is None:
			value = ''

		if module in self._module_settings:
			self._module_settings[module][name] = value

		self._settings_serializer.set(module, name, value, {})

	def get_module_settings(self, module):
		self._module_settings[module] = self._settings_serializer.getAllSettings(module)
		self._module_settings_template[module] = self._settings_template_serializer.getAllSettings(module)
		for name, value in self._module_settings_template[module].items():
			if name not in self._module_settings[module]:
				self._module_settings[module][name] = value
		return self._module_settings[module]

	def get_module_template_settings(self, module):
		return self._settings_template_serializer.getAllSettings(module)

	def save(self):
		self._settings_serializer.save(self._settings_file)

	def apply(self):
		data = self.get(SETTINGS.UH_MODULE, "Language")
		language = LANGUAGENAMES.get_by_value(data)
		change_language(language)

	def set_defaults(self):
		for module in self._settings_template_serializer.getModuleName():
			for setting_name in self._settings_template_serializer.getAllSettings(module):
				value = self._settings_template_serializer.get(module, setting_name)
				self.set(module, setting_name, value)
		self.save()

	def upgrade_settings(self):
		"""Upgrades the settings to a newer version necessary."""
		# if the settings file doesn't exist, force an update with
		# settings version 1 as default value
		current_version = self.get(SETTINGS.META_MODULE, self.SETTINGS_VERSION, 1)
		template_version = self._settings_template_serializer.get(SETTINGS.META_MODULE, self.SETTINGS_VERSION)
		if current_version != template_version:
			print('Discovered old settings file, auto-upgrading: {} -> {}'.format(
		          current_version, template_version))
			for module in self._settings_template_serializer.getModuleName():
				for setting_name in self._settings_template_serializer.getAllSettings(module):
					default_value = self._settings_template_serializer.get(module, setting_name)
					if self.get(module, setting_name, default=default_value) is default_value:
						self.set(module, setting_name, default_value)
			self.set(SETTINGS.META_MODULE, self.SETTINGS_VERSION, template_version)
			self.save()

	# settings

	def get_unknownhorizons_Language(self, value):
		if value is None: # the entry is None for empty strings
			value = ""
		return LANGUAGENAMES[value]

	def set_unknownhorizons_Language(self, value):
		return LANGUAGENAMES.get_by_value(value)


def detect_display_resolution():
	"""Best-effort detection of the desktop resolution.

	Used to pick a sensible default screen resolution on first game start
	(https://github.com/unknown-horizons/unknown-horizons/issues/1568).
	The desktop resolution is the best guess for user preference we have.

	@return: (width, height) tuple, or None if detection is not possible.
	"""
	# SDL2 is the most reliable source: FIFE itself is built on it, so it is
	# guaranteed to be available wherever the game runs.
	try:
		from ctypes import CDLL, Structure, byref, c_int, c_uint32, c_void_p
		from ctypes.util import find_library

		class SDL_DisplayMode(Structure):
			_fields_ = [('format', c_uint32),
			            ('w', c_int),
			            ('h', c_int),
			            ('refresh_rate', c_int),
			            ('driverdata', c_void_p)]

		SDL_INIT_VIDEO = 0x20
		libname = find_library('SDL2')
		if libname:
			sdl = CDLL(libname)
			# SDL init calls are reference counted, so initializing the video
			# subsystem here does not interfere with the engine init later.
			if sdl.SDL_InitSubSystem(SDL_INIT_VIDEO) == 0:
				try:
					mode = SDL_DisplayMode()
					if sdl.SDL_GetDesktopDisplayMode(0, byref(mode)) == 0:
						if mode.w > 0 and mode.h > 0:
							return (mode.w, mode.h)
				finally:
					sdl.SDL_QuitSubSystem(SDL_INIT_VIDEO)
	except Exception:
		pass

	# Fallback: tkinter ships with most desktop Python installs.
	try:
		import tkinter
		root = tkinter.Tk()
		root.withdraw()
		width, height = root.winfo_screenwidth(), root.winfo_screenheight()
		root.destroy()
		if width > 0 and height > 0:
			return (width, height)
	except Exception:
		pass

	return None
