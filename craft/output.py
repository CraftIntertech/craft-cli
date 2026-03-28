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
        click.echo("\t".join(headers))
        for row in rows:
            click.echo("\t".join(str(c) for c in row))


def print_success(msg):
    click.echo(click.style(msg, fg="green"))


def _format_value(val):
    """Format a value for display."""
    if val is None:
        return click.style("-", dim=True)
    if isinstance(val, bool):
        return click.style("Yes", fg="green") if val else click.style("No", fg="red")
    if isinstance(val, dict):
        return json.dumps(val, ensure_ascii=False)
    if isinstance(val, list):
        return ", ".join(str(v) for v in val) if val else click.style("-", dim=True)
    return str(val)


def _label(key):
    """Convert camelCase/snake_case key to readable label."""
    import re
    # camelCase → spaces
    label = re.sub(r'([a-z])([A-Z])', r'\1 \2', key)
    # snake_case → spaces
    label = label.replace("_", " ")
    return label.title()


def _flatten(obj):
    """Flatten nested dicts — child keys override parent on conflict."""
    result = {}
    nested = {}
    for key, val in obj.items():
        if isinstance(val, dict):
            nested.update(val)
        else:
            result[key] = val
    # Nested keys go first, then top-level (top-level wins on conflict)
    merged = {}
    merged.update(nested)
    merged.update(result)
    return merged


def print_item(data, fields=None):
    """Print a single item as formatted key-value pairs."""
    if isinstance(data, dict):
        obj = data.get("data", data)
    else:
        obj = data
    if not isinstance(obj, dict):
        print_json(data)
        return

    # Flatten nested dicts (e.g. vm.name → name)
    flat = _flatten(obj)

    items = fields if fields else list(flat.keys())

    # Find longest label for alignment
    labels = {k: _label(k) for k in items if k in flat}
    if not labels:
        print_json(data)
        return

    max_len = max(len(l) for l in labels.values())

    for key in items:
        if key not in flat:
            continue
        label = labels[key]
        val = _format_value(flat[key])
        click.echo(f"  {label:<{max_len}}  {val}")
