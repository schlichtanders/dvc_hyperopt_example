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
args = parser.parse_args()

# combine human-readable date suffix with utc timestamp in seconds
hyperoptfolder = f'hyperopt_{datetime.now().strftime("%Y-%m-%d")}_{int(time())}'

for i in range(2):
  runfolder = f".hyperopt/{hyperoptfolder}/run{i+1}"
  os.makedirs(runfolder)
  os.chdir(runfolder)
  check_output(["git", "clone", "../../../", "."])
  check_output(["git", "checkout", "-b", hyperoptfolder])
  check_output(["dvc", "repro", args.repro])
  check_output(["git", "commit", "-am", '"hyperopt run complete"'])
  check_output(["python", "./bin/git_push_set_upstream++.py"])
  os.chdir(origin)
