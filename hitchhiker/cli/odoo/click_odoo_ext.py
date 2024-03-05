from typing import Any

import click
import click_odoo  # type: ignore[import, import-untyped]
from click.decorators import _param_memo


# pylint: disable=invalid-name
class env_options(click_odoo.env_options):  # type: ignore[misc]
    def __call__(self, f: Any) -> Any:
        ret = super().__call__(f)
        _param_memo(
            f,
            click.Option(("--db_password",), help="database password", required=True),
        )
        _param_memo(
            f,
            click.Option(("--db_user",), help="database user", required=True),
        )
        _param_memo(
            f,
            click.Option(("--db_port",), help="database port", required=True, type=int),
        )
        _param_memo(
            f,
            click.Option(("--db_host",), help="database host", required=True),
        )
        return ret

    def _pop_params(self, ctx: Any) -> Any:
        super()._pop_params(ctx)
        ctx.params.pop("db_host", None)
        ctx.params.pop("db_port", None)
        ctx.params.pop("db_user", None)
        ctx.params.pop("db_password", None)

    def get_odoo_args(self, ctx: Any) -> Any:
        ret = super().get_odoo_args(ctx)
        ret.extend(["--db_host", ctx.params.get("db_host")])
        ret.extend(["--db_port", str(ctx.params.get("db_port"))])
        ret.extend(["--db_user", ctx.params.get("db_user")])
        ret.extend(["--db_password", ctx.params.get("db_password")])
        return ret
