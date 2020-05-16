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

import argparse
import importlib
import inspect
import builtins
import time
import json
import sys
from pyspark.sql import SparkSession


def TIME_START(step):
    stack = inspect.stack()
    c = stack[-2][0]
    c_module = inspect.getmodule(c)
    if not hasattr(c_module, "__timeinfo"):
        setattr(c_module, "timeinfo", {})
    c_module.timeinfo[step] = time.time()


def TIME_END(step):
    stack = inspect.stack()
    c = stack[-2][0]
    c_module = inspect.getmodule(c)
    assert hasattr(c_module, "timeinfo")
    start = c_module.timeinfo[step]
    dur = round(time.time() - start, 4)
    c_module.timeinfo[step] = dur


def TIME_INFO():
    stack = inspect.stack()
    c = stack[-2][0]
    c_module = inspect.getmodule(c)
    ret = c_module.timeinfo
    return ret


setattr(builtins, "TIME_START", TIME_START)
setattr(builtins, "TIME_END", TIME_END)
setattr(builtins, "TIME_INFO", TIME_INFO)


def write_output_time(output_file, test_time):
    test_time["version"] = "0.1.0"
    test_time["commit_id"] = "sasdasda"
    json_obj = json.dumps(test_time)
    json_file = open(output_file, "w")
    json_file.write(json_obj)
    json_file.close()


if __name__ == '__main__':
    from arctern_pyspark import register_funcs

    parse = argparse.ArgumentParser()
    parse.add_argument('-s --source_file', dest='source_file', nargs=1)
    parse.add_argument('-o --output_file', dest='output_file', nargs=1)
    parse.add_argument('-t --run_times', dest='run_times', nargs=1)
    parse.add_argument('-v --version', dest='version', nargs=1)

    args = parse.parse_args()
    source_file = args.source_file[0]
    output_file = args.output_file[0]
    run_times = int(args.run_times[0])
    version_commit = args.version[0]

    user_module = importlib.import_module("test_case." + (source_file.split(".")[0]).replace("/", "."),
                                          "test_case/" + source_file)
    spark_session = SparkSession \
        .builder \
        .appName("Python Arrow-in-Spark example") \
        .getOrCreate()
    spark_session.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
    conda_prefix = sys.prefix
    spark_session.conf.set("spark.executorEnv.PROJ_LIB", conda_prefix + "/share/proj")
    spark_session.conf.set("spark.executorEnv.GDAL_DATA", conda_prefix + "/share/gdal")
    spark_session.conf.set("PYSPARK_PYTHON", conda_prefix + "/bin/python")

    register_funcs(spark_session)

    all_time_info = {"version": version_commit.split("-")[0], "commit_id": version_commit.split("-")[-1],
                     "func_name": user_module.func_name}

    if hasattr(user_module, "spark_test"):
        data_df = spark_session.read.format("csv").option("header", False).option("delimiter", "|").schema(
            user_module.schema).load(user_module.csv_path).cache()
        data_df.createOrReplaceTempView(user_module.table_name)
        for times in range(run_times):
            time_info = {}
            begin_time = time.time()
            time_info["step"] = user_module.spark_test(spark_session)
            end_time = time.time()
            time_info["total_time"] = round(end_time - begin_time, 4)
            all_time_info["%s" % str(times)] = time_info
        print(user_module.func_name + " spark test run done!")

    else:
        data_df = spark_session.read.format("csv").option("header", False).option("delimiter", "|").schema(
            user_module.schema).load(user_module.csv_path).cache()
        data_df.createOrReplaceTempView(user_module.table_name)
        for times in range(run_times):
            time_info = {}
            begin_time = time.time()
            result_df = spark_session.sql(user_module.sql % (*user_module.col_name, user_module.table_name))
            result_df.createOrReplaceTempView("result")
            spark_session.sql("cache table result")
            spark_session.sql("uncache table result")
            end_time = time.time()
            time_info["total_time"] = round(end_time - begin_time, 4)
            time_step = {"step": round(end_time - begin_time, 4)}
            time_info["step"] = time_step
            all_time_info["%s" % str(times)] = time_info

        print(user_module.func_name + " spark test run done!")

    write_output_time(output_file, all_time_info)

