#!/usr/bin/python3

# Copyright 2020, Jan Ole von Hartz <hartzj@cs.uni-freiburg.de>.

from lxml import html
import click
import re
import requests

daphne_url = "https://daphne.informatik.uni-freiburg.de"
login_url = "https://daphne.informatik.uni-freiburg.de/login/"


@click.command()
@click.argument('url', nargs=1, required=True)
@click.argument('rz_user', nargs=1, required=True)
@click.argument('password', nargs=1, required=True)
def main(url, rz_user, password):
    """
    Extract the list of tutants from Daphne.
    Usually called from matching Makefile.

    Example use:
        utils/get_names.py https://daphne.informatik.uni-freiburg.de/ss2018/InformatikII/
    """
    # login stuff
    session_requests = requests.session()
    result = session_requests.get(login_url)
    tree = html.fromstring(result.text)
    auth_token = list(
        set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]
    lt_token = list(
        set(tree.xpath("//input[@name='lt']/@value")))[0]

    login_payload = {
        "csrfmiddlewaretoken": auth_token,
        "username": rz_user,
        "password": password,
        "lt": lt_token
    }

    headers = {
        "Referer": login_url,
    }

    result = session_requests.post(login_url, data=login_payload,
                                   headers=headers)

    # request page content
    html_content = session_requests.get(url, headers=dict(referer=url)).text

    assert url.startswith(daphne_url)
    course_string = url[len(daphne_url):]

    # Find names of all tutants in html, use the following regex
    # <td><a href="/ss2018/InformatikII/accounts/abc123/">abc123</a></td>
    matches = re.findall(
        """<td><a href=\"{}accounts\/([a-z]+[0-9]+)\/\">([a-z]+[0-9]+)<\/a><\/td>""".format(
        course_string), html_content, re.IGNORECASE)

    for match in matches:
        assert (match[0] == match[1])

    tutants = [match[0] for match in matches]

    if rz_user in tutants:
        tutants.remove(rz_user)

    print(' '.join(tutants))


if __name__ == "__main__":
    main()
