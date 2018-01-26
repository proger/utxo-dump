{ pythonPackages, fetchFromGitHub }:

pythonPackages.buildPythonPackage rec {
  name = "base58";
  src = fetchFromGitHub {
    owner = "keis";
    repo = "base58";
    rev = "043492f5cb7018851fd2890269c1dc66e0256367";
    sha256 = "0hylr79nq8rb3hisav4n330vbx6ynyal88n447iwfkyjqlijbskk";
  };

  doCheck = false;
}
