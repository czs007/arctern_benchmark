# Copyright (C) 2019-2020 Zilliz. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import arctern

csv_path = "data/st_curvetoline.csv"
col_num = 1
func_name = "st_curvetoline"
schema = "geos string"
col_name = ["geos"]

sql = "select ST_AsText(ST_CurveToLine(ST_GeomFromText(%s))) from %s"


def run(data):
    arctern.ST_AsText(arctern.ST_CurveToLine(arctern.ST_GeomFromText(data)))
