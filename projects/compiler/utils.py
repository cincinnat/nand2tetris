
def xml_symbol(symbol):
    values = {
        '>': '&gt;',
        '<': '&lt;',
        '&': '&amp;',
    }
    return values.get(symbol, symbol)
