import argparse
import subprocess
import os
from datetime import datetime
from time import time

def check_output(*args, **kwargs):
  return subprocess.check_output(*args, universal_newlines=True, **kwargs).strip()

origin = os.getcwd()

parser = argparse.ArgumentParser(description="hyperoptimization dummy routine")
parser.add_argument("repro")
parser.add_argument("-n", default=2)
args = parser.parse_args()

# combine human-readable date suffix with utc timestamp in seconds
hyperoptfolder = f'hyperopt/{datetime.now().strftime("%Y-%m-%d")}_{int(time())}'

check_output(["dvc", "push"])  # needed because we may need to access it from distributed runs

for i in range(args.n):
  runfolder = f".{hyperoptfolder}/run{i+1}"
  os.makedirs(runfolder)
  os.chdir(runfolder)
  print(f"cd {os.getcwd()}")
  check_output(["git", "clone", "../../../", "."])
  check_output(["git", "checkout", "-b", hyperoptfolder])
  check_output(["dvc", "repro", args.repro])
  check_output(["git", "commit", "-am", '"hyperopt run complete"'])
  check_output(["python", "./bin/git_push_set_upstream++.py"])
  check_output(["dvc", "push"])
  os.chdir(origin)

print(f"cd {os.getcwd()}")
check_output(["dvc", "fetch"])  # grap all the new data as even metrics are handled via dvc server
# TODO merge everything
# TODO metrics still not pushed accordingly