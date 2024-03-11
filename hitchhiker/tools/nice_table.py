from __future__ import annotations

from typing import Union


def gen_nice_table(rows: list[Union[list[str], str]]) -> str:
    generated = ""
    if len(rows) == 0:
        return generated
    longest = [0] * len(rows[0])
    for row in rows:
        if isinstance(row, str):
            continue
        if len(row) != len(longest):
            raise RuntimeError("gen_nice_table: no variable columns supported")
        for i, c in enumerate(row):
            longest[i] = max(longest[i], len(c))
    for row in rows:
        if isinstance(row, str):
            generated += f"{row}\n"
            continue
        for i, c in enumerate(row):
            spaces = ""
            if i < (len(row) - 1):
                spaces = f" {(longest[i] - len(c)) * ' '}"
            generated += f"{c}{spaces}"
        generated += "\n"
    return generated
