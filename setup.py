from setuptools import setup

setup(name='utxo-dump',
      version = '0.1',
      description='dump utxos from bitcoind chainstate to csv',
      author='proger',
      packages = ['cryptah'],
      author_email = 'vlad@kirillov.im',
      entry_points='''
      [console_scripts]
      utxo2csv = cryptah.utxo2csv:main
      hex2base58c = cryptah.hex2addr:main
      ''',
      install_requires=['python-bitcoinlib', 'base58', 'plyvel'])
