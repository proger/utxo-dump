import sys
from itertools import chain
import binascii

import base58

def main():
    inputs = chain(sys.argv[1:], sys.stdin) if not sys.stdin.isatty() else sys.argv[1:]
    for hex in inputs:
        hex = binascii.unhexlify(hex.strip())
        print(base58.b58encode_check(hex).decode('utf-8'))

if __name__ == '__main__':
    main()
