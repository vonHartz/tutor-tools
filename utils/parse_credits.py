"""
MIT License

Copyright (c) 2017 Danny Stoll <stolld@informatik.uni-freiburg.de>

Parse and dump credits to .json for all feedback-STUDENT.txt files in given directory.
Compatible for the Algorithmen and Datenstrukturen (SS2017) Course Bulk-Set Points
Daphne-Feature. Will use the STUDENT tag to extract information.


Usage: python36 CreditsParser.py [-h] [-r REGEX] sheet_number path

    positional arguments:
      sheet_number             number of excercise sheet to parse.
      path                     relative path to the feedback folder.

      credits_dir              relative path to the credits folder.
      json_prefix              Prefix of the name of the generated json. Name will be prefix-sheet_number.json


    optional arguments:
      -h, --help               show this help message and exit
      -r REGEX, --regex REGEX  python regex to extract credits from feedback-STUDENT.txt
"""

import argparse
import pathlib
import re
import json
import statistics as st


class CreditsParser(object):
    """Parse, compute statistics and dump credits to .json for all feedback-STUDENT.txt files
    in given directory.

    Args:
        sheet_number           (int):  excercise sheet number.
        feedback_path         (path):  path to match feedback-STUDENT.txt against.
        credits_regex_raw      (str):  matches the credits per line into group(1).

    Notes:
        Assumes all feedback files to have the format feedback-STUDENT.txt and assumes for them
        to be in current directory.
        Will add up all matched credits for a file to compute a students credit.
    """

    def __init__(self, sheet_number, feedback_path, json_prefix, credits_regex_raw=r'Aufgabe \d: (\d+)/\d'):
        self._sheet_string = 'uebungsblatt-'
        self._sheet_string += f'0{sheet_number}' if (sheet_number < 10) else f'{sheet_number}'

        self._credits_regex = re.compile(credits_regex_raw)
        self._feedback_path = feedback_path
        self._json_prefix = json_prefix

        self._serialisable_credits = dict()
        self._statistics_credits = list()  # no need to know the student name for statistics

    def _load_credits_from_path(self, student_shorthand, feedback_file):
        """Load the credit of given file.
        Args:
            student_shorthand (str): daphne Bulk-Set needs this information.
            feedback_file    (file): file to match self._credits_regex against.
        """
        credit = 0
        found_credit = False

        for line in feedback_file:
            # matches the credits per line into group(1)
            matchobj = self._credits_regex.match(line)
            if matchobj:
                found_credit = True
                credit += float(matchobj.group(1))

        if not found_credit:
            print(f'Warning: No credit was read in for Student {student_shorthand}, using 0 credits')
        self._serialisable_credits[student_shorthand] = {self._sheet_string: credit}
        self._statistics_credits += [credit]

    def load_all_credits(self):
        """Load the credit of every feedback file.

        Note:
            Expects group(1) of the Regex to contain the (task wise-)credit.
            Needs to be able to extract student id from filename, but can be
            rewritten via the .glob(..) and different feedback_path semantics.
        """
        for feedback in self._feedback_path.glob("feedback-*.txt"):
            # \S matches any non whitespace char
            student_shorthand = re.match(r'feedback-(\S*).txt', feedback.name).group(1)
            with feedback.open() as feedback_file:
                self._load_credits_from_path(student_shorthand, feedback_file)
        assert self._serialisable_credits, "No credits could be loaded"

    def credits_to_json(self, credits_dir):
        assert self._serialisable_credits, "No credits could be found to serialize"

        filename = credits_dir + "/" '{}-{}.json'.format(self._json_prefix,
                                                         self._sheet_string)
        with open(filename, "w+") as credits_file:
            json.dump(self._serialisable_credits, credits_file, indent=0)
        print(f'Credits dumped to {filename}')

    def print_statistics(self):
        assert self._statistics_credits, "No credits could be found to do statistics on"

        print(f'Count: {len(self._statistics_credits)}')
        print(f'Mean: {st.mean(self._statistics_credits): .2f}')
        print(f'Median: {st.median(self._statistics_credits)}')
        print(f'Stdev: {st.stdev(self._statistics_credits): .2f}')


def parse_arguments():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("sheet_number", help="number of excercise sheet to parse. ", type=int)
    argument_parser.add_argument("path", help="relative path to the feedback folder.")
    argument_parser.add_argument("credits_dir", help="relative path to the credits folder.")
    argument_parser.add_argument("json_prefix", help="Prefix of the name of the generated json.")
    argument_parser.add_argument("-r", "--regex", help="python regex to extract credits from feedback-STUDENT.txt")

    args = argument_parser.parse_args()
    sheet_number = args.sheet_number
    credits_regex = args.regex
    feedback_path_string = args.path
    credits_dir_string = args.credits_dir
    json_prefix = args.json_prefix
    print(feedback_path_string)

    assert sheet_number in range(1, 13), f'{sheet_number} is no valid sheet number.'
    return sheet_number, feedback_path_string, credits_dir_string, json_prefix, credits_regex


def main(sheet_number, feedback_path_string, credits_dir_string, json_prefix,
         credits_regex=None):
    feedback_path = pathlib.Path(feedback_path_string)
    if credits_regex:
        cc = CreditsParser(sheet_number, feedback_path, json_prefix, credits_regex)
    else:
        cc = CreditsParser(sheet_number, feedback_path, json_prefix)

    cc.load_all_credits()
    cc.print_statistics()
    cc.credits_to_json(credits_dir_string)


if __name__ == '__main__':
    args = parse_arguments()
    main(*args)
