#!/usr/bin/python3

# Original by ?
# Updated to Python3, uglified and made compatible with Makefile workflow by
# Jan Ole von Hartz <hartzj@cs.uni-freiburg.de>.


import click
import os
import json
import sys
import subprocess
import codecs
import re

files = ['erfahrungen.txt']
outputName = 'feedback-tutor' + '.txt'
dontCheck = ['.svn', 'private', 'public', '_Feedback', 'internal', 'sample_solutions']
directoryName = 'uebungsblatt-'
optionalFiles = ['Makefile']

hr1 = '=============\n\n'
hr2 = '-------------\n\n'
signature = "\nBei Fragen zur Korrektur (Punktabzüge usw.) bin ich jederzeit per Mail erreichbar.\n\n Jan <hartzj@cs.uni-freiburg.de>"

def load_tasks(task_file):
    """
    Reads a json file like this:
    {
        "1":
        {
          "a": 2,
          "b": 3,
          "c": 2,
          "c": 5
        },
        "2":
        {
          "c": 3,
          "c": 3
        },
        "3":
        {
          "a": 4,
          "b": 2,
          "c": 2,
          "c": 4
        }
    }
    """
    with open(task_file) as file:
        tasks = json.load(file)

    return tasks

def createFile(missing, illegal, empty, formatting='', template='',
               silent=False, override=False, log=False, add=False,
               useFlake=False):
    fileName = getFileName(override=override)
    outFile = open(fileName, 'w')

    global countValue

    if empty:
        outFile.write('Keine Abgabe vorhanden.\n\n')
        outFile.write('Du hast 0.0 von %.1f Punkten erreicht.\n' % points)
        outFile.write(signature + "")
    else:
        countValue += 1
        outFile.write(template+"\n")

        if len(missing) > 0:
            outFile.write('Missing files:\n')
            for line in missing:
                outFile.write('- '+line + '\n')
            outFile.write('\n')
        if len(illegal) > 0:
            outFile.write('Illegal files:\n')
            for line in illegal:
                outFile.write('- '+line + '\n')
        if useFlake and len(formatting) > 0:
            outFile.write('\nFlake8:\n')
            outFile.write(formatting)
            if not silent:
                print('Formatting issues found.')
        if log:
            try:
                logs = subprocess.check_output('svn log --limit=5', shell=True)
                logs = logs.decode('utf8')
                logs = str(logs)
                logs = re.sub('\r', '', logs)
                logs = re.sub('\n*$', '', logs)
                outFile.write('\nCommit-Logs:\n')
                outFile.write(logs)
                outFile.write('\n')
            except:
                pass

    outFile.close()
    if add:
        subprocess.call('svn add ' + fileName, shell=True)


def getFileName(override=False):
    if override:
        return outputName

    fileName = outputName
    new = 0
    commits = os.listdir()
    while fileName in commits:
        if new == 0:
            fileName = fileName.replace('.txt', '(0).txt')
        fileName = fileName.replace('(' + str(new) + ').txt',
                                    '(' + str(new+1) + ').txt')
        new += 1
    return fileName


def createTemplate(tasks, temp, points, recursiveCall, prefix):
    for key, value in tasks.items():
        temp += 'Aufgabe ' + prefix + key + '\n'
        temp += hr2 if recursiveCall else hr1
        if not isinstance(value, dict):
            temp += ">> XX / {} Punkte(n)".format(value) + '\n\n'
            points += value
        else:
            temp, points = createTemplate(value, temp, points, True, key)
    if not recursiveCall:
        temp += '\nDu hast XX von %.1f Punkten erreicht.\n' % points
        temp += signature
        temp += "\n" + 79*"="
    return (temp, points)

@click.command()
@click.argument('sheet_no', nargs=1, required=True)
@click.argument('task_file', nargs=1, required=True)
@click.argument('submissions_dir', nargs=1, required=True)
@click.argument('rz_short', nargs=1, required=True)
@click.option('-s', '--silent', is_flag=True)
@click.option('-n', '--nolog', is_flag=True)
@click.option('-o', '--override', is_flag=True)
@click.option('-a', '--add', is_flag=True)
@click.option('-f', '--noflake', is_flag=True)
def main(sheet_no, task_file, submissions_dir, rz_short, silent, nolog, override, add,
         noflake):
    """
    Create the feedback sheet for each submission of a given sheet.

    Example use:
        utils/feedback.py 01 .conf/task01.json submissions/ abc123
    """
    log = not nolog
    useFlake = not noflake

    template = ''
    points = 0.0
    global countValue
    countValue = 0
    missingFiles = 0

    dontCheck.append(rz_short)

    tasks = load_tasks(task_file)
    os.chdir(submissions_dir)
    dirs = [d for d in os.listdir() if os.path.isdir(d) and d not in dontCheck]
    template, points = createTemplate(tasks, template, points, False, '')
    for dir in dirs:
        if not silent:
            print("\n")
            print(dir)
            print(79*"=")
        os.chdir(dir)
        subprocess.call('svn update',shell=True)
        commits = os.listdir()
        if 'uebungsblatt-' + sheet_no not in commits:
            if not silent:
                print('uebungsblatt-' + sheet_no, 'not committed.\n')
            createFile([], [], True, silent=silent, override=override, log=log,
                       add=add, useFlake=useFlake, template=template)
            os.chdir('..')
            continue

        os.chdir('uebungsblatt-' + sheet_no)
        commits = os.listdir()
        if len(commits) == 0:
            os.chdir('..')
            if not silent:
                print('Nothing committed\n')
            createFile([], [], True, silent=silent, override=override, log=log,
                       add=add, useFlake=useFlake, template=template)
            os.chdir('..')
            continue

        missing = []
        if not silent:
            print('Missing files:')
        for f in files:
            if f not in commits:
                if not silent:
                    print(f)
                missing.append(f)
        if not silent and len(missing) == 0:
            print("No missing files")
        missingFiles = missingFiles + len(missing)

        illegal = []
        if not silent:
            print('\nIllegal files:')
        for c in commits:
            if c not in files + optionalFiles:
                if not silent:
                    pass
                    # print(c)
                # illegal.append(c)
        if not silent and len(illegal) == 0:
            print("No illegal files")

        formatting = ''
        try:
            for c in commits:
                if c.endswith('.py'):
                    p = subprocess.Popen('flake8 '+ c, stdout=subprocess.PIPE, shell=True)
                    flake = p.communicate()[0]
                    flake = flake.decode('utf8')
                    flake = str(flake)
                    flake = re.sub('\r', '', flake)
                    formatting += flake
        except Exception as flake:
            print("Flake8 couldn't run!\n"+str(flake))

        if not silent:
            print('')
        createFile(missing, illegal, False, formatting=formatting,
                   silent=silent, override=override, log=log, add=add,
                   useFlake=useFlake, template=template)
        os.chdir('..')
        # os.chdir('..')
        # createFile(missing, illegal, False, formatting)
        os.chdir('..')
    print("\n\n")
    print(30*"=")
    print(30*"=")
    print(str(countValue)+" Abgaben")
    print(str(missingFiles)+" Fehlende Dateien")

if __name__ == "__main__":
    main()
