import os
import sys
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET
from inspect import getmembers, isfunction


# Overall backlog length check
def gha_overall():
    key = os.environ['key']

    answer = requests.get("https://progress.opensuse.org/issues.xml?fixed_version_id=418"
                          + "&key=" + key)
    tree = ET.ElementTree(ET.fromstring(answer.content))
    root = tree.getroot()
    issue_count = int(root.attrib["total_count"])
    if issue_count > 90:
        exit(1)
    print("Overall backlog length is " + str(issue_count) + ", all good!")


# Workable backlog length check
def gha_workable():
    key = os.environ['key']
    answer = requests.get("https://progress.opensuse.org/issues.xml?fixed_version_id=418"
                          + "&status_id=12\&key=" + key)
    tree = ET.ElementTree(ET.fromstring(answer.content))
    root = tree.getroot()
    issue_count = int(root.attrib["total_count"])
    if issue_count > 40:
        print("Backlog has more than 40 'workable' tickets!")
        exit(1)
    elif issue_count < 10:
        print("Backlog has less than 10 'workable' tickets!")
        exit(1)
    print("'Workable' backlog length is " + str(issue_count) + ", all good!")


# Issues exceeding due date
def gha_exceed_due_date():
    key = os.environ['key']
    today = str((datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d'))
    answer = requests.get("https://progress.opensuse.org/issues.xml?fixed_version_id=418"
                          + "&status_id=!3|5|6&due_date=%3C%3D" + today + "&key=" + key)
    tree = ET.ElementTree(ET.fromstring(answer.content))
    root = tree.getroot()
    issue_count = int(root.attrib["total_count"])
    if issue_count > 0:
        print("There are tickets exceeding due date!")
        try:
            for poo in root.findall('issue'):
                print("https://progress.opensuse.org/issues/" + poo.find('id').text)
        except Exception:
            print("There was an error retrieving the issues exceeding due date")
            print("Please check " + "https://progress.opensuse.org/issues?query_id=514")
        exit(1)
    print("Issues exceeding due date are " + str(issue_count) + ", all good!")


# Untriaged issues
def gha_untriaged_qa():
    key = os.environ['key']
    answer_qa = requests.get("https://progress.opensuse.org/issues.xml?project_id=18&"
                             + "fixed_version_id=!*&key=" + key)
    answer_qap = requests.get("https://progress.opensuse.org/issues.xml?project_id=125&"
                              + "fixed_version_id=!*&key=" + key)
    tree = ET.ElementTree(ET.fromstring(answer_qa.content))
    root = tree.getroot()
    tree_p = ET.ElementTree(ET.fromstring(answer_qap.content))
    root_p = tree_p.getroot()
    issue_count = int(root.attrib["total_count"]) + int(root_p.attrib["total_count"])
    if issue_count > 0:
        print("There are untriaged tickets!")
        try:
            for poo in root.findall('issue'):
                print("https://progress.opensuse.org/issues/" + poo.find('id').text)
        except Exception:
            print(
                "Please check https://progress.opensuse.org/projects/qa/issues?query_id=576")
        exit(1)
    print("There are no untriaged tickets, all good!")


# Untriaged 'tools' tagged issues
def gha_untriaged_tools():
    key = os.environ['key']
    answer_qa = requests.get("https://progress.opensuse.org/issues.xml?project_id=18&"
                             + "fixed_version_id=!*&subject=~[tools]&key=" + key)
    answer_qap = requests.get("https://progress.opensuse.org/issues.xml?project_id=125&"
                              + "fixed_version_id=!*&subject=~tools&key=" + key)
    tree = ET.ElementTree(ET.fromstring(answer_qa.content))
    root = tree.getroot()
    tree_p = ET.ElementTree(ET.fromstring(answer_qap.content))
    root_p = tree_p.getroot()
    issue_count = int(root.attrib["total_count"]) + int(root_p.attrib["total_count"])
    if issue_count > 0:
        print("There are untriaged tools tagged tickets!")
        try:
            for poo in root.findall('issue'):
                print("https://progress.opensuse.org/issues/" + poo.find('id').text)
        except Exception:
            print(
                "Please check https://progress.opensuse.org/issues?" + "query_id=481")
        exit(1)
    print("There are no untriaged tools tagged tickets, all good!")


functions = {name: obj for name, obj in getmembers(sys.modules[__name__]) if (isfunction(
    obj) and name.startswith("gha"))}
functions[os.environ["fun"]]()
