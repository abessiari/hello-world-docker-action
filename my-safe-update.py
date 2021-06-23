#!/usr/bin/env python3

# Check Travis CI build status for the `master` branch of OBOFoundry/purl.obolibrary.org
# If `master` is green (i.e. all tests are passing),
# and the build number is greater than the current build
# (i.e. the last time we updated),
# then pull `master`, run Make, and update .current_build.

import difflib
import requests
import subprocess
import sys
from types import SimpleNamespace

def git_exec(repo_dir, args):
        import subprocess
        import os

        # command = ['git', '--work-tree=' + work_dir, '--git-dir=' + os.path.join(repo_dir, '.git')] + arg.split()
        command = ['git', '--work-tree=' + repo_dir] + args.split()

        with open(os.devnull, 'w') as devnull:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=devnull)
            code = result.returncode

            if code != 0:
                raise Exception('command failed:{},, code='.format(subprocess.list2cmdline(command), code))

            return result.stdout.decode('utf-8')

repo_slug = 'abessiari/hello-world-docker-action'

repo_dir = '/var/www/hello-world-docker-action'
branch = git_exec(repo_dir, 'branch').split()[1]
print(branch)

head_sha = git_exec(repo_dir, 'rev-parse HEAD').split()[0]
print(head_sha)
# https://github.com/abessiari/hello-world-docker-action.git
remote_head_sha = git_exec(repo_dir, 
                           'ls-remote https://github.com/{}.git {}'.format(repo_slug, branch)).split()[0]
print(remote_head_sha)

if remote_head_sha == head_sha:
    print('Nothing has been checked in into', branch)
    sys.exit(1)

api_url = 'https://api.github.com'
accept_header = {'Accept': 'application/vnd.github.v3+json'}
resp = requests.get('{}/repos/{}/actions/runs'.format(api_url, repo_slug), headers=accept_header)

if resp.status_code != requests.codes.ok:
    resp.raise_for_status()

result = SimpleNamespace(**resp.json())
workflow_runs = map(lambda x: SimpleNamespace(**x), result.workflow_runs)
workflow_run = next(filter(lambda x: x.head_sha == remote_head_sha, workflow_runs), None)
if not workflow_run:
    print('Workflow run not found for ', remote_head_sha)
    sys.exit(1)

assert workflow_run.head_branch == branch, 'branch check failed'
assert workflow_run.event == 'push', 'event check failed'

if workflow_run.status != 'completed' or workflow_run.conclusion != 'success':
    print('workflow run failed status/coclusion checks', workflow_run.status, '/', workflow_run.conclusion)
    sys.exit(1)

print("YYY:", workflow_run.id)

if subprocess.call(["git", "pull"]) != 0 or subprocess.call(["make"]) != 0:
    sys.exit(1)

sys.exit(0)
