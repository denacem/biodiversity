import locale

# Custom functions for Swiss number formatting
def format_swiss_number(number):
    formatted_number = locale.format('%0.2f', number, grouping=True)
    return formatted_number.replace(locale.localeconv()['decimal_point'], '.')

def format_swiss_number_sci(number):
    formatted_number = '{:.2e}'.format(number)
    return formatted_number.replace(locale.localeconv()['decimal_point'], '.')