# This is a set of Python keywords that cannot be used as prop names.
# Keywords for a particular version are obtained as follows:
# >>> import keyword
# >>> keyword.kwlist

python_keywords = {
    'and', 'elif', 'is', 'global', 'as', 'in', 'if', 'from', 'raise', 'for',
    'except', 'nonlocal', 'pass', 'finally', 'print', 'import', 'True', 'None',
    'return', 'exec', 'await', 'else', 'break', 'not', 'with', 'class',
    'assert', 'False', 'yield', 'try', 'while', 'continue', 'del', 'async',
    'or', 'def', 'lambda'
}

# This is a set of R reserved words that cannot be used as function
# argument names.
#
# Reserved words can be obtained from R's help pages by executing the
# statement below:
# > ?reserved

r_keywords = {
    'if', 'else', 'repeat', 'while', 'function', 'for', 'in', 'next', 'break',
    'TRUE', 'FALSE', 'NULL', 'Inf', 'NaN', 'NA', 'NA_integer_', 'NA_real_',
    'NA_complex_', 'NA_character_', '...'
}
