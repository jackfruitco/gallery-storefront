from django import template

register = template.Library()

@register.filter(is_safe=True)
def split_sentences(value, args=None):
    """Splits text into separate sentences, then returns the specified sentences."""
    value = value.split('. ')

    if args is None: return ". ".join(value[0:len(value)])
    else:
        args = args.replace(' ', '')
        args = args.split(':')
        if args[0] == '': args[0] = 0
        if args[1] == '': args[1] = len(value) + 1

    return ". ".join(value[int(args[0]):int(args[1])])
