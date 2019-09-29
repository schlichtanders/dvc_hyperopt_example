import argparse
import subprocess

def check_output(*args, **kwargs):
  return subprocess.check_output(*args, universal_newlines=True, **kwargs).strip()

def git_current_branchname():
  return check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])

def git_tracking_branch():
  return check_output(["git", "for-each-ref", "--format=%(upstream:short)", check_output(["git", "symbolic-ref", "-q", "HEAD"])])

parser = argparse.ArgumentParser(description="hallo")
parser.add_argument("branchname_without_incrementsuffix", nargs='?', default=None)
parser.add_argument("--max-increments", type=int, default=3)
args = parser.parse_args()

if args.branchname_without_incrementsuffix is None:
  args.branchname_without_incrementsuffix = git_current_branchname()


def get_new_increment(branchname_without_incrementsuffix):
  """ get suffix which does not exist yet, autoincrement if necessary """
  result = check_output(["git", "ls-remote", "origin", f"refs/heads/{branchname_without_incrementsuffix}/*"]).splitlines()
  print(result)
  if not result:
    return 1
  else:
    max_increment = 0
    for line in result:
      # the format is """commithash-tab-branchname"""
      # hence we can simply compare from the right
      row = line.split("/")
      if row[-2] == branchname_without_incrementsuffix:
        increment_string = row[-1]
        try:
          max_increment = max(max_increment, int(increment_string))
        except ValueError:  # TODO parse errormessage to be sure
          continue
    return max_increment + 1


def push_set_upstream_autoincrement(branchname_without_incrementsuffix, max_auto_increase=1):
  # second call should not increment again, hence we raise an Error if we find a remote tracking branch
  tracking_branch = git_tracking_branch()
  if tracking_branch:
    raise RuntimeError(f"The branch already tracks a remote branch ({tracking_branch}). "
      "Either delete the reference in order to use `git_push_set_upstream++`, or fall back to use plain `git push`.")
  
  increment = get_new_increment(branchname_without_incrementsuffix)

  for i in range(max_auto_increase):
    branchname_with_incrementsuffix = f"{branchname_without_incrementsuffix}/{increment + i}"
    try:
      command = ["git", "push", "--set-upstream", "origin", f"{branchname_without_incrementsuffix}:{branchname_with_incrementsuffix}"]
      print(" ".join(command))
      result = check_output(command)
      print(" ".join(command))
      return result
    except subprocess.CalledProcessError:
      continue
  
  raise RuntimeError(f"Reached maximum number of auto-increase attempts {max_auto_increase}. Set command-line argument like `--max-increments 10` to increase the limit.")


push_set_upstream_autoincrement(args.branchname_without_incrementsuffix, max_auto_increase=args.max_increments)
