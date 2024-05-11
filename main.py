import argparse
import base64
import configparser
import datetime
import itertools
import re
import subprocess

from jira import JIRA
import gitlab
from urllib.parse import urlparse


def init_jira(config):
    """JIRA initialization"""
    jira_config = config['jira']
    login = jira_config['login']
    password = base64.b64decode(jira_config['password'])
    jira_options = {'server': jira_config['server']}
    return JIRA(options=jira_options, basic_auth=(login, password)), jira_config['server']


def init_gitlab(config, gitlab_url):
    """Gitlab initialization and authentication"""
    if config.has_section(gitlab_url):
        gitlab_config = config[gitlab_url]
    else:
        gitlab_config = config['gitlab']

    url = gitlab_config['url']
    private_token = gitlab_config['private_token']

    gl = gitlab.Gitlab(url=url, private_token=private_token)
    gl.auth()
    return gl


def get_project_key(jira, name):
    """Get JIRA project key by name"""
    key = ""

    for p in jira.projects():
        if p.name == args.project:
            key = p.key
    return key


def get_release_issues(jira, project, release):
    """Get list of JIRA release issues"""
    jql = f'project = "{project}" and fixVersion = "{release}"'
    return jira.search_issues(jql, maxResults=0)


def get_commits(path, first, last, pattern):
    """Get list of git commits between git revisions. Experimental function. Requires local git installed"""

    data = subprocess.check_output([
        'git',
        '-C',
        path,  # 'd:/work/net/spb/armpabp',
        'log',
        '--pretty=format:%h %cd %s',
        '--date=format:%d.%m.%Y %H:%M:%S',
        '--abbrev=7',
        f'{first}..{last}'],
        encoding="utf-8"
    ).splitlines()

    # for i in data:
    #     print(i)

    commits = [[m,
                x[:7],
                x[8:27],
                datetime.datetime(
                    int(x[14:18]),
                    int(x[11:13]),
                    int(x[8:10]),
                    int(x[19:21]),
                    int(x[22:24]),
                    int(x[25:27])
                ),
                x[28:].rstrip()
                ] for x in data if pattern in x for m in re.findall(pattern + r"-\d+", x[28:].rstrip())
               ]

    # print(commits)
    commits = sorted(commits, key=lambda x: (x[0], x[3]))

    task_commits = itertools.groupby(commits, key=lambda x: x[0])

    return {task: sorted(commits, key=lambda x: x[3], reverse=True)[0][1] for task, commits in task_commits}


def get_gitlab_commits(path, first, last, pattern):
    """Get list of commits between two tags/branches by using gitlab compare function"""

    project = gl.projects.get(path[1:])
    compare_result = project.repository_compare(first, last)

    commits = [
        [
            m,
            x['short_id'],
            x['committed_date'],
            datetime.datetime.fromisoformat(x['committed_date']),
            x['message'].rstrip()
        ] for x in compare_result['commits'] if pattern in x['message']
        for m in re.findall(pattern + r"-\d+", x['message'].rstrip())
    ]

    # print(commits)
    commits = sorted(commits, key=lambda x: (x[0], x[3]))

    task_commits = itertools.groupby(commits, key=lambda x: x[0])

    return {task: sorted(commits, key=lambda x: x[3], reverse=True)[0][1] for task, commits in task_commits}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Gitlab project URL')
    parser.add_argument('first', help='First tag or branch name')
    parser.add_argument('last', help='Last tag or branch name')
    parser.add_argument('project', help='Jira project name')
    parser.add_argument('release', help='Jira release name')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('settings.ini')

    jira, jira_url = init_jira(config)

    try:
        project_key = get_project_key(jira, args.project)
    except Exception as e:
        print(f'Error while getting project key: {e}')
        exit(1)

    if project_key == "":
        print("Project not found")
        exit(1)

    try:
        issues = list(get_release_issues(jira, args.project, args.release))
    except Exception as e:
        print(f'Error while getting release issues: {e}')
        exit(1)

    if args.path.startswith('http'):
        o = urlparse(args.path)
        try:
            gl = init_gitlab(config, f"{o.netloc}")
        except Exception as e:
            print(f'Error while connecting to gitlab: {e}')
            exit(1)

        task_commits = get_gitlab_commits(o.path, args.first, args.last, project_key)
    else:
        task_commits = get_commits(args.path, args.first, args.last, project_key)

    no_commit_cnt = 0
    issue_keys = set()

    print("{:-^90}".format(" In release "))

    for task in issues:
        issue_keys.add(task.key)
        commit = task_commits.get(task.key, "-" * 8)
        issue = jira.issue(task.key)
        link = jira_url + "/browse/" + task.key
        print(f"{task} {commit.ljust(10)} {str(issue.fields.status).ljust(20)} {link}")
        if commit.startswith('-'):
            no_commit_cnt += 1

    print("{:-^90}".format(" Out of release "))

    out_of_release_cnt = 0

    for task, commit in task_commits.items():
        if task not in issue_keys:
            out_of_release_cnt += 1
            issue = jira.issue(task)
            link = jira_url + "/browse/" + task
            print(f"{task} {commit.ljust(10)} {str(issue.fields.status).ljust(20)} {link}")

    print('-' * 90)

    print('Tasks in Jira:', len(issues))
    print('Tasks in git:', len(task_commits))
    print('Tasks without commit:', no_commit_cnt)
    print('Tasks out of release:', out_of_release_cnt)
