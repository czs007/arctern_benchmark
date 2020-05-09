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

csv_path = "data/st_point.csv"
col_num = 2


def data_proc(csv_path):
    import csv
    import pandas as pd
    x = []
    y = []
    with open(csv_path, "r") as csv_file:
        spreader = csv.reader(csv_file, delimiter="|", quotechar="|")
        for row in spreader:
            x.append(float(row[0]))
            y.append(float(row[1]))
    return pd.Series(x), pd.Series(y)


def run(data1, data2):
    arctern.ST_AsText(arctern.ST_Point(data1, data2))
    print("st_point run done!")