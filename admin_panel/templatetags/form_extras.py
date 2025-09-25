from django import template

register = template.Library()


def _merge_attrs(widget, extra):
    base = (widget.attrs or {}).copy()
    # smart-merge class attribute
    if "class" in extra and "class" in base:
        extra = extra.copy()
        extra["class"] = (base["class"] + " " + extra["class"]).strip()
    base.update(extra)
    return base


@register.filter(name="add_class")
def add_class(field, css_classes: str):
    """
    Usage: {{ form.field|add_class:"input w-full" }}
    Appends CSS classes to the field widget without removing existing ones.
    """
    attrs = _merge_attrs(field.field.widget, {"class": css_classes})
    return field.as_widget(attrs=attrs)


@register.filter(name="attr")
def attr(field, args: str):
    """
    Usage:
      {{ form.field|attr:"placeholder:Andika jina lako,required" }}
      {{ form.email|attr:"autocomplete:email" }}
    Multiple attributes separated by comma. For boolean attrs, omit value.
    """
    parsed = {}
    for part in [a.strip() for a in (args or "").split(",") if a.strip()]:
        if ":" in part:
            k, v = part.split(":", 1)
            parsed[k.strip()] = v.strip()
        else:
            parsed[part] = True
    attrs = _merge_attrs(field.field.widget, parsed)
    return field.as_widget(attrs=attrs)


@register.filter(name="endswith")
def endswith(value, suffix):
    """
    Usage: {% if field.name|endswith:"_perm" %} ... {% endif %}
    """
    return str(value).endswith(str(suffix))
