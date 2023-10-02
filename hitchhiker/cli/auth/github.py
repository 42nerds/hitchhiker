import time
import requests
import json
import click


@click.command(short_help="Authenticate with GitHub")
@click.pass_context
def github(ctx: click.Context):
    """Get token from GitHub and save it in configuration"""
    oauth_client_id = "8fb737ec1cb768ded4c4"  # 42 N.E.R.D.S hitchhiker
    result = json.loads(
        requests.post(
            "https://github.com/login/device/code",
            headers={"Accept": "application/json"},
            data={"client_id": oauth_client_id, "scope": "repo"},
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
        raise Exception("unexpected response")
