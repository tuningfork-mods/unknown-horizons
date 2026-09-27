# ###################################################
# Copyright (C) 2008-2017 The Unknown Horizons Team
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

# Compatibility shims for FIFE 0.4.2 SWIG bindings, which don't export
# some typedef names the game expects. These aliases point at the exact
# same underlying C++ types.
try:
	from fife import fife as _fife_module
	if not hasattr(_fife_module, 'ScreenPoint'):
		# C++: typedef Point3D ScreenPoint
		_fife_module.ScreenPoint = _fife_module.Point3D
	if not hasattr(_fife_module, 'AudioSpaceCoordinate'):
		# C++: %template(AudioSpaceCoordinate) PointType3D<double>
		# (dropped by SWIG as duplicate of ExactModelCoordinate)
		_fife_module.AudioSpaceCoordinate = _fife_module.DoublePoint3D
	if not hasattr(_fife_module, 'ExactModelCoordinate'):
		# C++: typedef DoublePoint3D ExactModelCoordinate (modelcoords.h)
		_fife_module.ExactModelCoordinate = _fife_module.DoublePoint3D
	if not hasattr(_fife_module, 'ModelCoordinate'):
		# C++: typedef Point3D ModelCoordinate (modelcoords.h)
		_fife_module.ModelCoordinate = _fife_module.Point3D
except ImportError:
	pass
