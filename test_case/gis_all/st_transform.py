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

func_name = "st_transform"
csv_path = "data/single_point.csv"
col_num = 1
col_name = ["geos"]
schema = "geos string"

sql = "select ST_AsText(ST_Transform(ST_GeomFromText(%s), 'epsg:4326', 'epsg:3857')) from %s"


def python_test(data):
    TIME_START(func_name)
    arctern.ST_AsText(arctern.ST_Transform(arctern.ST_GeomFromText(data), "EPSG:4326", "EPSG:3857"))
    TIME_END(func_name)

    return TIME_INFO()
