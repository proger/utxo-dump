{ stdenv, python, pythonPackages, fetchurl, leveldb, libcxx }:
let
  inherit (stdenv.lib) licenses optionalAttrs;
in
pythonPackages.buildPythonPackage (rec {
  name = "plyvel-0.9";

  src = fetchurl {
    url = "mirror://pypi/p/plyvel/${name}.tar.gz";
    sha256 = "1scq75qyks9vmjd19bx57f2y60mkdr44ajvb12p3cjg439l96zaq";
  };

  propagatedBuildInputs = [ leveldb pythonPackages.pytest ];

  doCheck = true;

  meta = {
    description = "Fast and feature-rich Python interface to LevelDB";
    homepage = https://github.com/wbolster/plyvel;
    license = licenses.bsd3;
  };
} // optionalAttrs stdenv.isDarwin {
  NIX_CFLAGS_COMPILE = "-I${libcxx}/include/c++/v1";
  DYLD_LIBRARY_PATH = "${leveldb}/lib";
})
