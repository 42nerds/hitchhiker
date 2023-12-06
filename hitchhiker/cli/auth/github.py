import json
import time

import click
import requests


@click.command(short_help="Authenticate with GitHub")
@click.pass_context
def github(ctx: click.Context) -> None:
    """
    Gets a token from GitHub and saves it in the configuration.

    Description:
    This command retrieves a token from GitHub using the OAuth device flow.
    It prompts the user to open a URL and enter a code to complete the authentication process.
    The obtained token is then saved in the configuration as `GITHUB_TOKEN` for later use.

    """
    oauth_client_id = "8fb737ec1cb768ded4c4"  # 42 N.E.R.D.S hitchhiker
    result = json.loads(
        requests.post(
            "https://github.com/login/device/code",
            headers={"Accept": "application/json"},
            data={"client_id": oauth_client_id, "scope": "repo"},
            timeout=5,
        ).text
    )
    click.echo(
        f'Please open {result["verification_uri"]} and enter the code {result["user_code"]}'
    )
    while True:
        time.sleep(int(result["interval"]) + 2)
        second_result = json.loads(
            requests.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": oauth_client_id,
                    "device_code": result["device_code"],
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                timeout=5,
            ).text
        )
        if (
            "error" in second_result.keys()
            and second_result["error"] == "expired_token"
        ):
            click.secho("Timeout", err=True, fg="red")
            return
        if (
            "error" in second_result.keys()
            and second_result["error"] == "authorization_pending"
        ):
            continue
        if "access_token" in second_result.keys():
            ctx.obj["CONF"].set_key("GITHUB_TOKEN", second_result["access_token"])
            click.secho("Success!", err=False, fg="green")
            return
        raise click.UsageError("unexpected response")
