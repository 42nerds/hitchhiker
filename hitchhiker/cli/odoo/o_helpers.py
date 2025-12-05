from click_odoo import odoo  # type: ignore[import, import-untyped]


def get_db_name() -> str:
    val = odoo.tools.config["db_name"]
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        if len(val) != 1:
            raise RuntimeError(f"len(db_name) != 1 db_name: '{repr(val)}'")
        return val[0]  # type: ignore[no-any-return]
    raise RuntimeError(f"could not parse Odoo db_name '{repr(val)}'")
