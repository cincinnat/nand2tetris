import io
import tokenize
import pytest

import jack_tokenizer


@pytest.mark.parametrize('symbol', jack_tokenizer.symbols)
def test_symbols(symbol):
    t = jack_tokenizer.Tokenizer()
    tokens = t.tokenize(io.StringIO(symbol))
    tok = next(tokens)
    assert tok.type == 'symbol'
    assert tok.value == symbol


@pytest.mark.parametrize('keyword', jack_tokenizer.keywords)
def test_keywords(keyword):
    t = jack_tokenizer.Tokenizer()
    tokens = t.tokenize(io.StringIO(keyword))
    tok = next(tokens)
    assert tok.type == 'keyword'
    assert tok.value == keyword


def test_string_const():
    t = jack_tokenizer.Tokenizer()

    tokens = t.tokenize(io.StringIO('"qwerty uiop"'))
    tok = next(tokens)
    assert tok.type == 'string_const'
    assert tok.value == '"qwerty uiop"'


@pytest.mark.parametrize('string', [
        '"qwerty',
        'qwerty"',
        '"qwerty',
        'qwe"rty',
        '"qwe"rty"',
        '"qwe\nrty"',
    ])
def test_malformed_string_const(string):
    t = jack_tokenizer.Tokenizer()

    with pytest.raises(jack_tokenizer.TokenizerError):
        tokens = t.tokenize(io.StringIO(string))
        list(tokens)


def test_int_const():
    t = jack_tokenizer.Tokenizer()
    tokens = t.tokenize(io.StringIO('1234 12b'))

    tok = next(tokens)
    assert tok.type == 'int_const'
    assert tok.value == 1234
    
    with pytest.raises(jack_tokenizer.TokenizerError):
        next(tokens)


def test_tokenizer():
    source = '''
            class Point {
               field int _x;
               field int _y;

               constructor Point new(int x, int y) {
                   let _x = x;
                   let _y = y;
               }

               method void dispose() {
                   do Memory.deAlloc();
               }

               method int getX() { return _x; }
               method int getY() { return _y; }
            }
        '''

    t = jack_tokenizer.Tokenizer()
    tokens = t.tokenize(io.StringIO(source))
    tokens = map(lambda t: t.value, tokens)
    tokens = list(tokens)

    # expected = source.split()
    expected = tokenize.tokenize(io.BytesIO(source.encode()).readline)
    expected = map(lambda t: t.string, expected)
    expected = filter(str.strip, expected)
    next(expected)  # spkip the 'utf-8' token
    expected = list(expected) + ['EOF']

    assert tokens == expected


def test_single_line_comment():
    t = jack_tokenizer.Tokenizer()
    tokens = t.tokenize(io.StringIO('''
            // comment
            x, // comment
            y
        '''))

    assert next(tokens).value == 'x'
    assert next(tokens).value == ','
    assert next(tokens).value == 'y'


def test_multi_line_comment():
    t = jack_tokenizer.Tokenizer()
    tokens = t.tokenize(io.StringIO('''
            /* comment
             * comment
             */
            x, /* comment */
            y
        '''))

    assert next(tokens).value == 'x'
    assert next(tokens).value == ','
    assert next(tokens).value == 'y'
