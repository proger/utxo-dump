import sys
from itertools import chain
import ctypes

from bitcoin.core.script import CScript
from bitcoin.core.script import CScriptTruncatedPushDataError, CScriptInvalidError
from bitcoin.core.key import CPubKey, CECKey
from bitcoin.core.key import _ssl
import bitcoin.core.script as s
from bitcoin.core import x, b2x


_ssl.ERR_load_crypto_strings()


def ssl_get_error():
    errno = _ssl.ERR_get_error()
    errmsg = ctypes.create_string_buffer(120)
    _ssl.ERR_error_string_n(errno, errmsg, 120)
    return str(errmsg.value)


def pk_scriptdecompress(pk):
    # https://github.com/bitcoin/bitcoin/blob/5961b23898ee7c0af2626c46d5d70e80136578d3/src/compressor.cpp#L118
    xpk = bytes(bytearray([pk[0] - 2]) + pk[1:])

    pk = CPubKey(xpk)
    cec = CECKey()
    cec.set_compressed(True)
    res = cec.set_pubkey(pk)
    if res is None:
        raise Exception(ssl_get_error())
    cec.set_compressed(False)
    pubkey = cec.get_pubkey()
    return CPubKey(pubkey, _cec_key=cec)


def p2sh(shash):
    """
    Pays To Script Hash
    """
    assert len(shash) == 20
    return CScript([s.OP_HASH160,
                    len(shash),
                    shash,
                    s.OP_EQUAL])


def p2pkh(pkhash):
    """
    Pays To PubKey Hash
    """
    assert len(pkhash) == 20
    return CScript([s.OP_DUP,
                    s.OP_HASH160,
                    len(pkhash),
                    pkhash,
                    s.OP_EQUALVERIFY,
                    s.OP_CHECKSIG])


def p2pk(pk):
    """
    https://github.com/bitpay/bitcore-lib/blob/master/docs/publickey.md#compressed-vs-uncompressed
    pk is compressed, includes X value and parity
    """
    assert len(pk) == 33 or len(pk) == 65
    return CScript([len(pk),
                    pk,
                    s.OP_CHECKSIG])


def decompress(nsize, data):
    # https://github.com/bitcoin/bitcoin/blob/5961b23898ee7c0af2626c46d5d70e80136578d3/src/script/script.h#L32
    MAX_SCRIPT_SIZE = 10000

    # https://github.com/bitcoin/bitcoin/blob/5961b23898ee7c0af2626c46d5d70e80136578d3/src/compressor.h#L31-L37
    nSpecialScripts = 6

    # https://github.com/bitcoin/bitcoin/blob/5961b23898ee7c0af2626c46d5d70e80136578d3/src/compressor.cpp#L88
    if nsize == 0x00:
        return 'p2pkh', p2pkh(data)
    elif nsize == 0x01:
        return 'p2sh', p2sh(data)
    elif nsize in [0x02, 0x03]:
        pk = bytearray([nsize]) + data
        return 'p2pk', p2pk(bytes(pk))
    elif nsize in [0x04, 0x05]:
        pkc = bytearray([nsize]) + data
        return 'p2pk', p2pk(pk_scriptdecompress(bytes(pkc)))
    else:
        # https://github.com/bitcoin/bitcoin/blob/5961b23898ee7c0af2626c46d5d70e80136578d3/src/compressor.h#L80
        size = nsize - nSpecialScripts
        if size > MAX_SCRIPT_SIZE:
            return 'oversize', CScript([s.OP_RETURN])

        return 'unk', CScript(data[:size])


def script_repr(cscript):
    def _repr(o):
        if isinstance(o, bytes):
            return "<{}>".format(b2x(o))
        else:
            return repr(o)

    ops = []
    i = iter(cscript)
    while True:
        op = None
        try:
            op = _repr(next(i))
        except CScriptTruncatedPushDataError as err:
            op = '%s...<ERROR: %s>' % (_repr(err.data), err)
            break
        except CScriptInvalidError as err:
            op = '<ERROR: %s>' % err
            break
        except StopIteration:
            break
        finally:
            if op is not None:
                ops.append(op)

    return ' '.join(ops)


if __name__ == '__main__':
    inputs = chain(sys.argv[1:], sys.stdin) if not sys.stdin.isatty() else sys.argv[1:]

    if not inputs:
        print('usage: python -mcryptah.script <hex script> ...', file=sys.stderr)
        print('   or: cat hex-scripts | python -mcryptah.script', file=sys.stderr)
        sys.exit(1)

    for script in inputs:
        script = script.strip()
        print(script_repr(CScript(x(script))))
