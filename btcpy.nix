{ pythonPackages, fetchFromGitHub, base58 }:

pythonPackages.buildPythonPackage rec {
  name = "btcpy";
  src = fetchFromGitHub {
    owner = "chainside";
    repo = "btcpy";
    rev =  "337185e7d4bb00ca235d2242b7cbd0e1c3487963";
    sha256 = "1nz49dp9zk0xw25ihbh21ffgb34c1y7ww63zivdy7ds8i0yssppk";
  };

  propagatedBuildInputs = [ pythonPackages.ecdsa base58 ];

  doCheck = false;
}
