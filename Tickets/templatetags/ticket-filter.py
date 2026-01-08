from django import template
from django.utils.safestring import mark_safe
import difflib

register = template.Library()

@register.filter
def format_with_highlight(old_value, new_value):
    old_text = str(old_value) if old_value not in [None, ""] else "(None)"
    new_text = str(new_value) if new_value not in [None, ""] else "(None)"

    if old_text == new_text:
        return mark_safe(f'"{new_text}" -> "{new_text}"')

    diff = difflib.SequenceMatcher(None, old_text, new_text)

    old_highlighted = []
    new_highlighted = []

    for tag, i1, i2, j1, j2 in diff.get_opcodes():
        if tag == 'equal':
            old_highlighted.append(old_text[i1:i2])
            new_highlighted.append(new_text[j1:j2])
        elif tag == 'replace':
            old_highlighted.append(f'<span class="char-removed">{old_text[i1:i2]}</span>')
            new_highlighted.append(f'<span class="char-added">{new_text[j1:j2]}</span>')
        elif tag == 'delete':
            old_highlighted.append(f'<span class="char-removed">{old_text[i1:i2]}</span>')
        elif tag == 'insert':
            new_highlighted.append(f'<span class="char-added">{new_text[j1:j2]}</span>')

    return mark_safe(f'''
    "<span>{"".join(old_highlighted)}</span>" 
    <i class="fas fa-arrow-right mx-1"></i> 
    "<span>{"".join(new_highlighted)}</span>"
    ''')