import json

import click

try:
    from tabulate import tabulate

    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

# Status color mapping for common status values
_STATUS_COLORS = {
    "running": "green", "active": "green", "online": "green", "enabled": "green",
    "open": "green", "paid": "green", "completed": "green", "success": "green",
    "stopped": "red", "inactive": "red", "offline": "red", "disabled": "red",
    "deleted": "red", "failed": "red", "error": "red", "closed": "red",
    "expired": "red", "suspended": "red",
    "pending": "yellow", "creating": "yellow", "starting": "yellow",
    "stopping": "yellow", "rebooting": "yellow", "resizing": "yellow",
    "reinstalling": "yellow", "processing": "yellow",
}


def _colorize_status(val):
    """Apply color to known status values."""
    if isinstance(val, str):
        color = _STATUS_COLORS.get(val.lower())
        if color:
            return click.style(val, fg=color)
    return str(val)


def print_json(data):
    """Print data as formatted JSON."""
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


def print_table(rows, headers):
    """Print data as a table."""
    # Colorize status columns
    status_cols = {i for i, h in enumerate(headers) if h.lower() in ("status", "state")}
    if status_cols:
        colored_rows = []
        for row in rows:
            new_row = list(row)
            for col_idx in status_cols:
                if col_idx < len(new_row):
                    new_row[col_idx] = _colorize_status(new_row[col_idx])
            colored_rows.append(new_row)
        rows = colored_rows

    if HAS_TABULATE:
        click.echo(tabulate(rows, headers=headers, tablefmt="simple"))
    else:
        click.echo("\t".join(headers))
        for row in rows:
            click.echo("\t".join(str(c) for c in row))


def print_success(msg):
    click.echo(click.style(msg, fg="green"))


def print_warning(msg):
    click.echo(click.style(msg, fg="yellow"))


def print_page_info(data, page=None, limit=None):
    """Print pagination info if available in response."""
    if not isinstance(data, dict):
        return
    meta = data.get("meta", data.get("pagination", {}))
    if isinstance(meta, dict):
        total = meta.get("total", meta.get("totalItems"))
        total_pages = meta.get("totalPages", meta.get("pages"))
        current = meta.get("page", meta.get("currentPage", page))
        if total is not None and current is not None:
            page_info = f"  Page {current}"
            if total_pages:
                page_info += f" of {total_pages}"
            page_info += f" ({total} total)"
            click.echo(click.style(page_info, dim=True))
            return
    # Fallback: infer from list length
    if page and limit:
        inner = data.get("data", data)
        if isinstance(inner, list):
            count = len(inner)
            if count > 0:
                click.echo(click.style(f"  Page {page} ({count} items)", dim=True))
        elif isinstance(inner, dict):
            items = inner.get("items", inner.get("vms", inner.get("accounts", [])))
            if isinstance(items, list) and items:
                click.echo(click.style(f"  Page {page} ({len(items)} items)", dim=True))


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

    # Keys that should get status coloring
    status_keys = {"status", "state"}

    for key in items:
        if key not in flat:
            continue
        label = labels[key]
        if key.lower() in status_keys:
            val = _colorize_status(flat[key])
        else:
            val = _format_value(flat[key])
        click.echo(f"  {label:<{max_len}}  {val}")
