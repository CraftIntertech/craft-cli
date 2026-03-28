import json

import click

try:
    from tabulate import tabulate

    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def print_json(data):
    """Print data as formatted JSON."""
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


def print_table(rows, headers):
    """Print data as a table."""
    if HAS_TABULATE:
        click.echo(tabulate(rows, headers=headers, tablefmt="simple"))
    else:
        # Fallback: tab-separated
        click.echo("\t".join(headers))
        for row in rows:
            click.echo("\t".join(str(c) for c in row))


def print_success(msg):
    click.echo(click.style(msg, fg="green"))


def print_item(data, fields=None):
    """Print a single item as key-value pairs."""
    if isinstance(data, dict):
        obj = data.get("data", data)
    else:
        obj = data
    if not isinstance(obj, dict):
        print_json(data)
        return
    if fields:
        for key in fields:
            if key in obj:
                click.echo(f"{key}: {obj[key]}")
    else:
        for key, val in obj.items():
            click.echo(f"{key}: {val}")
