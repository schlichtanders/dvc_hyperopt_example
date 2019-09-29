import argparse
import subprocess

class MyArg:
  pass

args = MyArg()
args.metric = "score.txt"


def check_output(*args, **kwargs):
  return subprocess.check_output(*args, universal_newlines=True, **kwargs).strip()


parser = argparse.ArgumentParser(description="Merge a complete subfolder by picking the best one according to the specified metric.")
parser.add_argument("branch_subfolder")
parser.add_argument("--min", dest='optimizer', action='store_const', const=min, help="minimize given metric")
parser.add_argument("--max", dest='optimizer', action='store_const', const=max, help="maximize given metric")
parser.add_argument("--metric")

args = parser.parse_args()
assert not args.branch_subfolder.endswith("/"), "assuming branch_subfolder is given without trailing slash"


# get metrics information from dvc
metrics = check_output(["dvc", "metrics", "show", "-a", args.metric]).splitlines()
print("\n".join(metrics))

branchnames = metrics[0::2]  # every odd should be a branch name
assert all(not name.startswith("\t") for name in branchnames), "More than one metric selected, aborting."  # every second row should refer to branchname if only one metric was choosen
scores = [float(m[len(args.metric)+3:]) for m in metrics[1::2]]  # every even should be a metric value prepended by "metricname: "

metrics_subset = [name, score for name, score in zip(branchnames, scores) if name.startswith(args.branch_subfolder)]
best_branch = args.optimizer(metrics_subset, key=lambda t:t[1])[0]

check_output(["git", "merge", "--no-ff", best_branch]).splitlines()

branchnames_subset = [m[0] for m in metrics_subset]

check_output(["git", "merge", "--strategy=ours", *branchnames_subset])


