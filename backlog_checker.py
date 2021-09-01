import os
import sys
import json
from datetime import datetime, timedelta
from inspect import getmembers, isfunction
import requests


# Icons used for PASS or FAIL in the md file
result_icons = {"pass": "&#x1F49A;", "fail": "&#x1F534;"}
# Links for various backlog queries to be used in the md file
query_links = {
    "Overall Backlog": "[Overall Backlog](https://progress.opensuse.org/issues?query_id=230)",
    "Workable Backlog": "[Workable Backlog](https://progress.opensuse.org/issues?query_id=478)",
    "Exceeding Due Date": "[Exceeding Due Date](https://progress.opensuse.org/issues?query_id=514)",
    "Untriaged QA": "[Untriaged QA](https://progress.opensuse.org/projects/qa/issues?query_id=576)",
    "Untriaged Tools Tagged": "[Untriaged Tools Tagged](https://progress.opensuse.org/issues?query_id=481)"
}


# Initialize a blank md file to replace the current README
def initialize_md():
    with open("index.md", "a") as md:
        md.write("# Backlog Status\n\n")
        md.write("**Latest Run:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " GMT\n")
        md.write("*(Please refresh to see latest results)*\n\n")
        md.write("Backlog Query | Number of Issues | Limits | Status\n--- | --- | --- | ---\n")


# Append individual results to md file
def results_to_md(item, number, limits, status):
    with open("index.md", "a") as md:
        md.write("| " + item + " | " + number + " | " + limits + " | " + status + "\n")


# Overall backlog length check
def gha_overall():
    key = os.environ['key']

    answer = requests.get("https://progress.opensuse.org/issues.json?fixed_version_id=418"
                          + "&key=" + key)
    root = json.loads(answer.content)
    issue_count = int(root["total_count"])
    if issue_count > 100:
        print("Backlog has more than 100 overall tickets!")
        print("Please check https://progress.opensuse.org/issues?query_id=230")
        results_to_md(query_links["Overall Backlog"], str(issue_count), "<100",
                      result_icons["fail"])
        exit(1)
    print("Overall backlog length is " + str(issue_count) + ", all good!")
    results_to_md(query_links["Overall Backlog"], str(issue_count), "<100",
                  result_icons["pass"])


# Workable backlog length check
def gha_workable():
    key = os.environ['key']
    answer = requests.get("https://progress.opensuse.org/issues.json?fixed_version_id=418"
                          + "&status_id=12\&key=" + key)
    root = json.loads(answer.content)
    issue_count = int(root["total_count"])
    backlog_ok = False
    if issue_count > 40:
        print("Backlog has more than 40 'workable' tickets!")
        results_to_md("Workable Backlog", str(issue_count), ">10, <40",
                      result_icons["fail"])
    elif issue_count < 10:
        print("Backlog has less than 10 'workable' tickets!")
        results_to_md("Workable Backlog", str(issue_count), ">10, <40",
                      result_icons["fail"])
    else:
        backlog_ok = True
    if not backlog_ok:
        print("Please check https://progress.opensuse.org/issues?query_id=478")
        exit(1)
    print("'Workable' backlog length is " + str(issue_count) + ", all good!")
    results_to_md(query_links["Workable Backlog"], str(issue_count), ">10, <40",
                  result_icons["pass"])


# Issues exceeding due date
def gha_exceed_due_date():
    key = os.environ['key']
    today = str(datetime.today().strftime('%Y-%m-%d'))
    answer = requests.get("https://progress.opensuse.org/issues.json?fixed_version_id=418"
                          + "&status_id=!3|5|6&due_date=%3C%3D" + today + "&key=" + key)
    root = json.loads(answer.content)
    issue_count = int(root["total_count"])
    if issue_count > 0:
        print("There are tickets exceeding due date!")
        try:
            for poo in root['issues']:
                print("https://progress.opensuse.org/issues/" + str(poo['id']))
        except Exception:
            print("There was an error retrieving the issues exceeding due date")
            print("Please check " + "https://progress.opensuse.org/issues?query_id=514")
        else:
            if issue_count > len(root['issues']):
                print("there are more issues, check https://progress.opensuse.org/issues?"
                      + "query_id=514")
        results_to_md(query_links["Exceeding Due Date"], str(issue_count), "<1",
                      result_icons["fail"])
        exit(1)
    print("Issues exceeding due date are " + str(issue_count) + ", all good!")
    results_to_md(query_links["Exceeding Due Date"], str(issue_count), "<1",
                  result_icons["pass"])


# Untriaged issues
def gha_untriaged_qa():
    key = os.environ['key']
    answer_qa = requests.get("https://progress.opensuse.org/issues.json?project_id=18&"
                            + "fixed_version_id=!*&key=" + key)
    answer_qap = requests.get("https://progress.opensuse.org/issues.json?project_id=125&"
                              + "fixed_version_id=!*&key=" + key)
    root = json.loads(answer_qa.content)
    root_p = json.loads(answer_qap.content)
    issue_count = int(root["total_count"]) + int(root_p["total_count"])
    if issue_count > 0:
        print("There are untriaged tickets!")
        try:
            for poo in root['issues']:
                print("https://progress.opensuse.org/issues/" + str(poo['id']))
            for poo in root_p['issues']:
                print("https://progress.opensuse.org/issues/" + str(poo['id']))
        except Exception:
            print(
                "Please check https://progress.opensuse.org/projects/qa/issues?query_id=576")
        else:
            if issue_count > len(root['issues']) + len(root_p['issues']):
                print("there are more issues, check https://progress.opensuse.org/issues?"
                      + "query_id=576")
        results_to_md(query_links["Untriaged QA"], str(issue_count), "<1",
                      result_icons["fail"])
        exit(1)
    print("There are no untriaged tickets, all good!")
    results_to_md(query_links["Untriaged QA"], str(issue_count), "<1",
                  result_icons["pass"])


# Untriaged 'tools' tagged issues
def gha_untriaged_tools():
    key = os.environ['key']
    answer_qa = requests.get("https://progress.opensuse.org/issues.json?project_id=18&"
                             + "fixed_version_id=!*&subject=~[tools]&key=" + key)
    answer_qap = requests.get("https://progress.opensuse.org/issues.json?project_id=125&"
                              + "fixed_version_id=!*&subject=~tools&key=" + key)
    root = json.loads(answer_qa.content)
    root_p = json.loads(answer_qap.content)
    issue_count = int(root["total_count"]) + int(root_p["total_count"])
    if issue_count > 0:
        print("There are untriaged tools tagged tickets!")
        try:
            for poo in root['issues']:
                print("https://progress.opensuse.org/issues/" + str(poo['id']))
            for poo in root_p['issues']:
                print("https://progress.opensuse.org/issues/" + str(poo['id']))
        except Exception:
            print(
                "Please check https://progress.opensuse.org/projects/qa/issues?query_id=481")
        else:
            if issue_count > len(root['issues']) + len(root_p['issues']):
                print("There are more issues, check https://progress.opensuse.org/issues?"
                      + "query_id=481")
        exit(1)
    print("There are no untriaged tools tagged tickets, all good!")
    results_to_md(query_links["Untriaged Tools Tagged"], str(issue_count), "<1",
                  result_icons["pass"])


functions = {name: obj for name, obj in getmembers(sys.modules[__name__]) if (isfunction(
    obj) and name.startswith("gha"))}
if "fun" not in os.environ:
    initialize_md()
else:
    functions[os.environ["fun"]]()
