{ pythonPackages, fetchFromGitHub, openssl }:

pythonPackages.buildPythonPackage rec {
  name = "python-bitcoinlib";
  src = fetchFromGitHub {
    owner = "petertodd";
    repo = "python-bitcoinlib";
    rev =  "ca1ef885573676d13d60b1376cf5abc60f2ce5dd";
    sha256 = "0ja6dljxmd1s63nh9rlic4w149cxg2m1qj94jvmcb62y9mkg0ljl";
  };
  propagatedBuildInputs = [ openssl ];
}
