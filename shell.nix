let
  #channels = builtins.fetchTarball https://d3g5gsiof5omrk.cloudfront.net/nixpkgs/nixpkgs-18.03pre117623.29f4775103/nixexprs.tar.xz;
  channels = builtins.fetchTarball https://d3g5gsiof5omrk.cloudfront.net/nixos/unstable/nixos-18.03pre126063.95880aaf062/nixexprs.tar.xz;
  nixpkgs = import channels { config.allowUnfree = true; };
  #nixpkgs = import <nixpkgs> {};
in
{ pkgs ? nixpkgs }:
let
  inherit (pkgs) lib stdenv;

  python = pkgs.python36;
  pythonPackages = pkgs.python36Packages;

  python-bitcoinlib = pkgs.callPackage ./python-bitcoinlib.nix {
    inherit pythonPackages;
  };

  base58 = pkgs.callPackage ./base58.nix {
    inherit pythonPackages;
  };

  plyvel = pkgs.callPackage ./plyvel.nix {
    inherit python pythonPackages;
  };

  utxo-dump = pkgs.callPackage ./. {
    inherit pythonPackages python plyvel base58 python-bitcoinlib;
  };

  btcpy = pkgs.callPackage ./btcpy.nix {
    inherit pythonPackages base58;
  };
in
pkgs.stdenv.mkDerivation {
  name = "shell";

  buildInputs = with pkgs; [
    pv
    python
    pythonPackages.ipython

    pythonPackages.ecdsa
    utxo-dump
    btcpy
  ];

  shellHook = ''
    # workaround some darwin + python36 bug
    export DYLD_LIBRARY_PATH="${pkgs.leveldb}/lib"

    export NIX_PATH="nixpkgs=${toString pkgs.path}"
    echo -n 'nixpkgs version: '
    nix-instantiate --eval -E '(import <nixpkgs> {}).lib.nixpkgsVersion'
  '';
}
