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
import os
import sys
import subprocess
import yaml
from python import python_benchmark


def switch_conda_environment(version, commit_id):
    conda_env_name = (version + "-" + commit_id).replace("*", "")
    conda_env_dict = {"name": conda_env_name, "channels": ["conda-forge", "arctern-dev"],
                      "dependencies": ["libarctern=" + version + "=" + commit_id,
                                       "arctern=" + version + "=" + commit_id,
                                       "arctern-spark=" + version + "=" + commit_id,
                                       "pyyaml"]}
    with open("conf/arctern.yaml", "w") as conda_env_f:
        yaml_obj = yaml.dump(conda_env_dict)
        conda_env_f.write(yaml_obj)

    status = os.system("conda env create -f conf/arctern.yaml")
    if status in [0, 256]:
        original_conda_file = open("conf/arctern_version.conf", "r")
        original_conda_env_list = original_conda_file.readlines()
        delete_current_conda_env_file = open("conf/arctern_version.conf", "w")
        delete_current_conda_env_list = "".join(original_conda_env_list[1:])
        delete_current_conda_env_file.write(delete_current_conda_env_list)
        original_conda_file.close()
        delete_current_conda_env_file.close()
        conda_prefix = subprocess.check_output("conda env list | grep %s" % conda_env_name, shell=True).decode(
            'utf-8').split(" ")[-1].replace("\n", "")
        exec_python_path = conda_prefix + "/bin/python"
        for n, e in enumerate(sys.argv):
            if e == "-w":
                sys.argv[n + 1] = "False"
            if e == "-c":
                sys.argv[n+1] = "False"
        os.execlp(exec_python_path, "arctern test", *sys.argv)
        sys.exit(0)
    else:
        print("create conda environment failed!")
        sys.exit(1)


def conf_spark_env():
    import re
    spark_submit_path = subprocess.check_output("which spark-submit", shell=True).decode('utf-8').replace("\n", "")
    spark_conf_path = os.path.join("/".join(spark_submit_path.split("/")[0:-1]), "../conf")
    conf_env_path = sys.prefix
    spark_env_f = open(spark_conf_path + "/spark-env.sh", "r+")
    source_env_text = spark_env_f.readlines()
    pyspark_path_exist = False
    for i in range(len(source_env_text)):
        if re.search("PYSPARK_PYTHON", source_env_text[i]):
            source_env_text[i] = "export PYSPARK_PYTHON=%s/bin/python" % conf_env_path
            pyspark_path_exist = True
    if not pyspark_path_exist:
        source_env_text.append("export PYSPARK_PYTHON=%s/bin/python" % conf_env_path)
    target_env_file = open(spark_conf_path + "/spark-env.sh", "w+")
    target_env_file.writelines(source_env_text)
    target_env_file.close()

    spark_default_f = open(spark_conf_path + "/spark-defaults.conf", "r+")
    source_default_text = spark_default_f.readlines()
    proj_exist = False
    gdal_exist = False
    for i in range(len(source_default_text)):
        if re.search("spark.executorEnv.PROJ_LIB", source_default_text[i]):
            source_default_text[i] = "spark.executorEnv.PROJ_LIB %s/share/proj" % conf_env_path
            proj_exist = True
        if re.search("spark.executorEnv.PROJ_LIB", source_default_text[i]):
            source_default_text[i] = "spark.executorEnv.GDAL_DATA %s/share/gdal" % conf_env_path
            gdal_exist = True
    if not proj_exist:
        source_default_text.append("spark.executorEnv.PROJ_LIB %s/share/proj" % conf_env_path)
    if not gdal_exist:
        source_default_text.append("spark.executorEnv.GDAL_DATA %s/share/gdal" % conf_env_path)
    target_default__file = open(spark_conf_path + "/spark-defaults.conf", "w+")
    target_default__file.writelines(source_default_text)
    target_default__file.close()


def spark_test(source_file, output_file, run_times, commit_id):
    conf_spark_env()
    command = "spark-submit ./spark/spark_benchmark.py -s %s -o %s -t %s -v %s" % (
        source_file, output_file, run_times, commit_id)
    os.system(command)


def run_test(scheduler_file, version_commit_id, test_spark, test_python):

    output_path = "output/" + version_commit_id
    with open(scheduler_file, "r") as f:
        for line in f:
            source_file = line.split(" ")[0]
            output_file = line.split(" ")[1]

            test_case = output_file.replace(output_file.split("/")[-1], "")
            out_python_path = output_path + "/python/" + test_case
            out_spark_path = output_path + "/spark/" + test_case
            if not os.path.exists(out_python_path):
                os.makedirs(out_python_path)
            if not os.path.exists(out_spark_path):
                os.makedirs(out_spark_path)

            user_module = importlib.import_module("test_case." + (source_file.split(".")[0]).replace("/", "."),
                                                  "test_case/" + source_file)

            if test_spark:
                spark_test(source_file, out_spark_path + output_file.split("/")[-1].replace("\n", ""),
                           run_time, version_commit_id)

            if test_python:
                python_benchmark.python_test(out_python_path + "/" + output_file.split("/")[-1].replace("\n", ""),
                                             user_module, run_time, version_commit_id)


def tag_commit_build_time():
    import arctern
    import re
    version_info = arctern.version().split("\n")
    build_time = ""
    commit_id = sys.prefix.replace("\n", "").split("/")[-1]
    for info in version_info:
        if re.search("build time", info):
            build_time = info.replace("build time : ", "")

    version_build_time = {"build_time": build_time,
                          "commit_id": commit_id}

    f = open("result_html/version_build_time.txt", "r")
    lines = f.readlines()
    version_exist = False
    for line in lines:
        if re.search(str(version_build_time), line):
            version_exist = True

    with open("result_html/version_build_time.txt", "w+") as file:
        file.writelines(lines)
        if not version_exist:
            file.writelines(str(version_build_time) + "\n")


if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument('-f --file', dest='file', nargs=1, default=None)
    parse.add_argument('-w --switch_env', dest='switch_env', nargs=1, default=False)
    parse.add_argument('--python', dest="python", nargs='*')
    parse.add_argument('--spark', dest="spark", nargs='*')
    parse.add_argument('--times', dest='times', nargs=1)
    parse.add_argument('-v --version', dest='version', nargs=1)
    parse.add_argument('--commit_id', dest='commit_id', nargs=1)

    args = parse.parse_args()

    if args.switch_env is not None:
        switch_env = eval(args.switch_env[0])
    else:
        switch_env = False

    run_time = eval(args.times[0])
    version = args.version[0]
    commit_id = args.commit_id[0]
    if switch_env:
        switch_conda_environment(version, commit_id)
    else:
        if args.file is not None:
            scheduler_file = args.file[0]
        else:
            scheduler_file = "scheduler/gis_only/gis_test.txt"
        test_spark = False
        test_python = False
        if args.python is not None:
            test_python = True
        if args.spark is not None:
            test_spark = True

        tag_commit_build_time()
        run_test(scheduler_file, version + "-" + commit_id, test_spark, test_python)
