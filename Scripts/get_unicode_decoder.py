import ast


def remove_double_backslashes(a):
    return ast.literal_eval(str(a).replace('\\\\', '\\'))


def unicode_decoder(b):
    result = remove_double_backslashes(b)
    result = result.decode()
    return result


if __name__ == "__main__":
    a = b'\\xe5\\xb7\\xb2\\xe6\\x9c\\x89\\xe5\\xb7\\xa5\\xe4\\xbd\\x9c\\xe8\\xa1\\xa8\\xe4\\xbd\\xbf\\xe7\\x94\\xa8' \
        b'\\xe3\\x80\\x8cClaimed W+1 Account Opening Report\\xe3\\x80\\x8d\\xe9\\x80\\x99\\xe5\\x80\\x8b\\xe5\\x90' \
        b'\\x8d\\xe7\\xa8\\xb1\\xe3\\x80\\x82\\xe8\\xab\\x8b\\xe8\\xbc\\xb8\\xe5\\x85\\xa5\\xe5\\x85\\xb6\\xe4\\xbb\\' \
        b'x96\\xe5\\x90\\x8d\\xe7\\xa8\\xb1\\xe3\\x80\\x82'
    b = unicode_decoder(a)
    print(b)

