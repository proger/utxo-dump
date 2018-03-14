{ python, pythonPackages, callPackage, leveldb, plyvel, python-bitcoinlib, base58, binutils-raw, openssl }:

let
  python-bitcoinlib = callPackage ./python-bitcoinlib.nix {
    inherit pythonPackages;
  };

  base58 = callPackage ./base58.nix {
    inherit pythonPackages;
  };

  plyvel = callPackage ./plyvel.nix {
    inherit python pythonPackages;
  };
in pythonPackages.buildPythonPackage {
  name = "utxo-dump";
  src = builtins.filterSource (path: type: baseNameOf path != "chainstate") ./.;
  doCheck = false;

  propagatedBuildInputs = [ python-bitcoinlib base58 plyvel ];

  postFixup = ''
    wrapProgram $out/bin/utxo2csv \
      --prefix DYLD_LIBRARY_PATH : "${leveldb}/lib:${openssl.out}/lib" \
      --prefix LD_LIBRARY_PATH : "${leveldb}/lib:${openssl.out}/lib" \
      --prefix PATH : "${binutils-raw.bintools}/bin"
  '';
}
