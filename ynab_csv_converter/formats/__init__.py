

def validate_line(line, column_patterns):
    for name, regex in column_patterns.items():
        value = getattr(line, name)
        if regex.match(value) is None:
            msg = ("Column `{column}' with value `{value}' did not match pattern {pattern}"
                   .format(column=name, value=value, pattern=regex.pattern))
            raise Exception(msg)
