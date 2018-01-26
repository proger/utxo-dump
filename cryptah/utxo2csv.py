import sys
from .chainstate import every_utxo, UTXO

def main():
    kwargs = {}
    for chainstate_dir in sys.argv[1:]:
        kwargs = dict(chainstate_dir=chainstate_dir)

    # csv header
    print(','.join(UTXO._fields))

    for utxo in every_utxo(**kwargs):
        print(','.join(map(str, utxo)))

if __name__ == '__main__':
    main()
