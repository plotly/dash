import keyword

python_keywords = set(keyword.kwlist)

# This is a set of R reserved words that cannot be used as function
# argument names.
#
# Reserved words can be obtained from R's help pages by executing the
# statement below:
# > ?reserved

r_keywords = {
    "if",
    "else",
    "repeat",
    "while",
    "function",
    "for",
    "in",
    "next",
    "break",
    "TRUE",
    "FALSE",
    "NULL",
    "Inf",
    "NaN",
    "NA",
    "NA_integer_",
    "NA_real_",
    "NA_complex_",
    "NA_character_",
    "...",
}
