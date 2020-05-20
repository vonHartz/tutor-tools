#!/usr/bin/python3

# Copyright 2020, Jan Ole von Hartz <hartzj@cs.uni-freiburg.de>.

from lxml import html
import click
import requests

daphne_url = "https://daphne.informatik.uni-freiburg.de"
login_url = "https://daphne.informatik.uni-freiburg.de/login/"


@click.command()
@click.argument('url', nargs=1, required=True)
@click.argument('json_file', nargs=1, required=True)
@click.argument('rz_user', nargs=1, required=True)
@click.argument('password', nargs=1, required=True)
def main(url, json_file, rz_user, password):
    """
    Post the generated JSON to the Daphne bulk page.

    Example use:
        utils/get_names.py https://daphne.informatik.uni-freiburg.de/ss2018/InformatikII/solutions/bulk/ credits/credits-01.json
    """
    with open(json_file, 'r') as file:
        json_txt = file.read()

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

    result = session_requests.post(login_url, data = login_payload,
                                   headers=headers)

    # request page content
    result = session_requests.get(url, headers=dict(referer=url)).text

    assert url.startswith(daphne_url)
    course_string = url[len(daphne_url):]

    json_payload = {
        "csrfmiddlewaretoken": auth_token,
        "data": json_txt,
        "lt": lt_token
    }

    headers = {
        "Referer": url,
    }

    result = session_requests.post(url, data=json_payload, headers=headers)


if __name__ == "__main__":
    main()
