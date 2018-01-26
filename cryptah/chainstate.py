from binascii import hexlify, unhexlify
from collections import namedtuple

import plyvel

from . import script


UTXO = namedtuple('UTXO', ('tx_id_be',
                           'output_index',
                           'is_coinbase',
                           'height',
                           'satoshi',
                           'type',
                           'scriptPubKey'))


def every_utxo(chainstate_dir='chainstate'):
    """
    Generator that yields UTXO read from the chainstate LevelDB database.
    """

    db = plyvel.DB(chainstate_dir, compression=None)  # Change with path to chainstate

    # Load obfuscation key (if it exists)
    o_key = db.get((unhexlify("0e00") + b"obfuscate_key"))

    assert o_key

    # The leading byte indicates the length of the key (8 byte by default). If there is no key,
    # 8-byte zeros are used (since the key will be XORed with the given values).
    o_key = o_key[1:]

    for key, value in db.iterator(prefix=b'C'):
        serialized_outpoint = key[1:]
        serialized_coin = deobfuscate_value(o_key, value)
        yield decode_utxo(serialized_coin, serialized_outpoint)

    db.close()


def deobfuscate_value(key, value):
    key_len = len(key)
    return bytearray(x ^ key[i % key_len] for i, x in enumerate(value))


def decode_utxo(coin, outpoint):
    """Decode a LevelDB serialized UTXO for Bitcoin core v0.15 onwards.

    outpoint: COutPoint
    coin: Coin
    """

    # https://github.com/bitcoin/bitcoin/blob/v0.15.0/src/txdb.cpp#L40-L53
    assert len(outpoint) >= 33
    # Get the transaction id (LE) by parsing the next 32 bytes of the outpoint.
    # Convert to BE right here by reversing.
    tx_id_be = outpoint[:32][::-1]
    tx_index = read_varint(outpoint[32:])[0]

    # https://github.com/bitcoin/bitcoin/blob/v0.15.0/src/coins.h#L67-L73
    code, offset = read_varint(coin)
    height = code >> 1
    is_coinbase = code & 0x01

    amount, offset = read_varint(coin, offset)
    amount = txout_decompressamount(amount)

    # https://github.com/bitcoin/bitcoin/blob/v0.15.0/src/compressor.h#L73
    nsize, offset = read_varint(coin, offset)

    script_type, cscript = script.decompress(nsize, coin[offset:])

    return UTXO(tx_id_be=hexlify(tx_id_be).decode('utf-8'),
                output_index=tx_index,
                is_coinbase=is_coinbase,
                height=height,
                satoshi=amount,
                type=script_type,
                scriptPubKey=hexlify(cscript).decode('utf-8'))


def read_varint(buf, offset=0):
    "Decode MSB base-128 VarInt."

    # https://github.com/bitcoin/bitcoin/blob/v0.13.2/src/serialize.h#L306-L328
    n = 0

    for i, byte in enumerate(buf[offset:]):
        n = n << 7 | byte & 0x7F

        # MSB b128 Varints have set the bit 128 for every byte but the last one,
        # indicating that there is an additional byte following the one being read.
        if byte & 0x80:
            n += 1
        else:
            return n, offset + i + 1


def txout_decompressamount(x):
    "Decompress the Satoshi amount."

    # https://github.com/bitcoin/bitcoin/blob/v0.13.2/src/compressor.cpp#L161#L185

    if x == 0:
        return 0
    x -= 1
    e = x % 10
    x //= 10
    if e < 9:
        d = (x % 9) + 1
        x //= 9
        n = x * 10 + d
    else:
        n = x + 1
    while e > 0:
        n *= 10
        e -= 1
    return n
