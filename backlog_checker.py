import os
import sys
import json
from datetime import datetime, timedelta
from inspect import getmembers, isfunction
import requests


# Icons used for PASS or FAIL in the md file
result_icons = {"pass": "&#x1F49A;", "fail": "&#x1F534;"}

# Initialize a blank md file to replace the current README
def initialize_md():
    with open("index.md", "a") as md:
        md.write("# Backlog Status\n\n")
        md.write("**Latest Run:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " GMT\n")
        md.write("*(Please refresh to see latest results)*\n\n")
        md.write("Backlog Query | Number of Issues | Limits | Status\n--- | --- | --- | ---\n")

data = {
    'gha_overall': {
        'title': 'Overall Backlog',
        'url': 'https://progress.opensuse.org/issues.json?query_id=230',
        'max': 99,
        'link': 'https://progress.opensuse.org/issues?query_id=230',
        'type': 'backlog',
    },
    'gha_workable': {
        'title': 'Workable Backlog',
        'url': 'https://progress.opensuse.org/issues.json?query_id=478',
        'max': 39,
        'min': 11,
        'link': 'https://progress.opensuse.org/issues?query_id=478',
        'type': 'backlog',
    },
    'gha_exceed_due_date': {
        'title': 'Exceeding Due Date',
        'url': 'https://progress.opensuse.org/issues.json?query_id=514',
        'max': 0,
        'link': 'https://progress.opensuse.org/issues?query_id=514',
        'type': 'zero',
    },
    'gha_untriaged_qa': {
        'title': 'Untriaged QA',
        'url': 'https://progress.opensuse.org/issues.json?query_id=576&project_id=115',
        'max': 0,
        'link': 'https://progress.opensuse.org/projects/qa/issues?query_id=576&project_id=115',
        'type': 'zero',
    },
    'gha_untriaged_tools': {
        'title': 'Untriaged Tools Tagged',
        'url': 'https://progress.opensuse.org/issues.json?query_id=481',
        'max': 0,
        'link': 'https://progress.opensuse.org/issues?query_id=481',
        'type': 'zero',
    },
}


# Append individual results to md file
def results_to_md(conf, number, status):
    mdlink = '[' + conf['title'] + '](' + conf['link'] + ')'
    lessthan = conf['max'] + 1
    limits = '<' + str(lessthan)
    if 'min' in conf:
        limits += ', >' + str(conf['min'] - 1)
    with open("index.md", "a") as md:
        md.write(mdlink + " | " + str(number) + " | " + limits + " | " + status + "\n")


def get_json(conf):
    key = os.environ['key']
    answer = requests.get(conf['url'] + "&key=" + key)
    return json.loads(answer.content)


def list_issues(conf, root):
    try:
        for poo in root['issues']:
            print("https://progress.opensuse.org/issues/" + str(poo['id']))
    except Exception:
        print("There was an error retrieving the issues " + conf['title'])
        print("Please check " + conf['link'])
    else:
        issue_count = int(root["total_count"])
        if issue_count > len(root['issues']):
            print("there are more issues, check " + conf['link'])


def failure_more(conf):
    print(conf['title'] + " has more than " + str(conf['max']) + " tickets!")
    print("Please check " + conf['link'])
    return False


def failure_less(conf):
    print(conf['title'] + " has less than " + str(conf['min']) + " tickets!")
    print("Please check " + conf['link'])
    return False


def check_backlog(conf):
    root = get_json(conf)
    issue_count = int(root["total_count"])
    if issue_count > conf['max']:
        res = failure_more(conf)
    elif 'min' in conf and issue_count < conf['min']:
        res = failure_less(conf)
    else:
        res = True
        print(conf['title'] + " length is " + str(issue_count) + ", all good!")
    return (res, issue_count)


def check_zero(conf):
    root = get_json(conf)
    issue_count = int(root["total_count"])
    if issue_count > conf['max']:
        res = False
        print("There are " + conf['title'] + " tickets!")
        list_issues(conf, root)
    else:
        res = True
        print("There are no " + conf['title'] + " tickets, all good!")
    return (res, issue_count)


def check_query(name):
    conf = data[name]
    if conf['type'] == 'backlog':
        res = check_backlog(conf)
    else:
        res = check_zero(conf)
    if res[0] is False:
        results_to_md(conf, res[1], result_icons["fail"])
        exit(1)
    results_to_md(conf, res[1], result_icons["pass"])


if "fun" not in os.environ:
    initialize_md()
else:
    check_query(os.environ["fun"])
