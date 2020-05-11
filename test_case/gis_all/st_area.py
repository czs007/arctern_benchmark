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

func_name = "st_area"
csv_path = "data/single_polygon.csv"
col_num = 1
schema = "geos string"

sql = "select ST_Area(ST_GeomFromText(data)) from %s"


def spark_test(spark, csv_path):
    data_df = spark.read.format("csv").option("header", False).option("delimiter", "|").schema(
        "geos string").load(csv_path).cache()
    data_df.createOrReplaceTempView(func_name)
    result_df = spark.sql(sql % func_name)
    result_df.createOrReplaceTempView("result")
    spark.sql("cache table result")
    spark.sql("uncache table result")


def python_test(data):
    arctern.ST_Area(arctern.ST_GeomFromText(data))
    print("st_area run done!")
