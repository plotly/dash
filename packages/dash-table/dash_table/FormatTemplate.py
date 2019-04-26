from .Format import Format, Group, Scheme, Sign, Symbol


def money(decimals, sign=Sign.default):
    return Format(
        group=Group.yes,
        precision=decimals,
        scheme=Scheme.fixed,
        sign=sign,
        symbol=Symbol.yes
    )


def percentage(decimals, rounded=False):
    if not isinstance(rounded, bool):
        raise TypeError('expected rounded to be a boolean')

    rounded = Scheme.percentage_rounded if rounded else Scheme.percentage
    return Format(
        scheme=rounded,
        precision=decimals
    )
