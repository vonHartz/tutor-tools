#!/usr/bin/python3

"""
Copyright 2018 University of Freiburg
Sebastian Holler <hollers@tf.uni-freiburg.de>

Uglified and made compatible with Makefile workflow in 2020 by
Jan Ole von Hartz <hartzj@cs.uni-freiburg.de>.
"""

import click
import os
import pathlib
import shutil

feedback_filename = 'feedback-tutor.txt'
temp_dir = 'temp917'
dont_check = ['.svn', 'private', 'public', '_Feedback', 'internal',
              'sample_solutions', temp_dir]

feedback_regex = '\"Du hast (\\d+\\.\\d) von\"'


@click.command()
@click.argument('sheet_no', nargs=1, required=True)
@click.argument('rz_short', nargs=1, required=True)
@click.argument('submissions_dir', nargs=1, required=True)
@click.argument('credits_dir', nargs=1, required=True)
@click.argument('json_prefix', nargs=1, required=True)
@click.argument('parse_credits_script', nargs=1, required=True)
def main(sheet_no, rz_short, submissions_dir, credits_dir, json_prefix,
         parse_credits_script):
    """
    Gather the student's scores in json file for bulk upload.

    Example use:
        utils/create_credits.py 01 abc123 submissions credits credits utils/parse_credits.py
    """

    dont_check.append(rz_short)
    script_dir = pathlib.Path().absolute()
    os.chdir(submissions_dir)
    os.makedirs(temp_dir)
    gather_feedback(sheet_no)
    os.chdir(script_dir)
    os.system('python3 {} -r {} {} {} {} {}'.format(
        parse_credits_script, feedback_regex, str(int(sheet_no)),
        submissions_dir + "/" + temp_dir, credits_dir, json_prefix))
    shutil.rmtree(script_dir / submissions_dir / temp_dir)


def gather_feedback(sheet_no):
    """Gathers all feedback in a temporary folder which is required for parse_credits.py

    Args:
        sheet_number           (str):  two digit excercise sheet number.
    """

    paths = [
        p for p in os.listdir() if os.path.isdir(p) and p not in dont_check]
    for path in paths:
        src = path + '/uebungsblatt-' + sheet_no + '/' + feedback_filename
        dest = temp_dir + '/feedback-' + path + '.txt'
        try:
            shutil.copy2(src, dest)
        except FileNotFoundError:
            print('FileNotFoundError: feedback for student ' + path + ' not found')


if __name__ == "__main__":
    main()
