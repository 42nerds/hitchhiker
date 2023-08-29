import click

import click_odoo
from click_odoo import odoo


@click.group()
@click.option("-c", "--config", default="./odoo.conf", help="path to odoo configuration file", type=click.Path(exists=True))
@click.pass_context
def odoo(ctx, config):
    """Odoo related commands"""
    ctx.obj['ODOO_CONF'] = config

@odoo.command()
@click.pass_context
def backup(ctx):
    """Backup Odoo"""
    pass

@odoo.command()
@click.pass_context
def staging(ctx):
    """Backup Odoo"""
    
