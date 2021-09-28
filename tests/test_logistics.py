# -*- coding: utf-8 -*-

#    Copyright (C) 2017-2021 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pandas as pd
import pytest

from dtocean_maintenance.logistics import (EquipmentType,
                                           VesselType,
                                           _copy_equipment_dict,
                                           _copy_vessel_dict)


@pytest.fixture
def equipmentdict():
    
    dummy = {"a": [1, 2, 3],
             "b": [4, 5, 6]}
    
    return {"toaster": EquipmentType("toaster", pd.DataFrame(dummy))}


@pytest.fixture
def vesseldict():
    
    dummy = {"a": [1, 2, 3],
             "b": [4, 5, 6]}
    
    return {"battleship": VesselType("battleship", pd.DataFrame(dummy))}


def test_copy_equipment_dict(equipmentdict):
    
    copy = _copy_equipment_dict(equipmentdict)
    
    assert set(copy) == set(equipmentdict)
    assert copy["toaster"] is not equipmentdict["toaster"]
    assert copy["toaster"].panda is not equipmentdict["toaster"].panda
    assert set(copy["toaster"].panda.columns) == set(["a", "b"])


def test_copy_vessel_dict(vesseldict):
    
    copy = _copy_vessel_dict(vesseldict)
    
    assert set(copy) == set(vesseldict)
    assert copy["battleship"] is not vesseldict["battleship"]
    assert copy["battleship"].panda is not vesseldict["battleship"].panda
    assert set(copy["battleship"].panda.columns) == set(["a", "b"])
