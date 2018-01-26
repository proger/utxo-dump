# utxo-dump

Dump UTXOs from bitcoind (v0.15.x or newer) chainstate to csv.

Quick start (you need [Nix 1.11.15](https://nixos.org/nix/) or newer):

```
$ git clone https://github.com/cryptah/utxo-dump ~/utxo-dump
$ cd ~/utxo-dump
$ nix-shell

## dump the chainstate database to CSV:

[nix-shell:~/utxo-dump]$ utxo2csv ~/.bitcoin/chainstate | pv > utxo.csv

## selectively parse pubkey scripts to human-readable list of opcodes:

[nix-shell:~/utxo-dump]$ tail utxo.csv | awk -F, '{print $7}' | python -mcryptah.script
```

The resulting csv file will be around 3x larger than the chainstate database, so plan accordingly.
