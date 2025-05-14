{
  description = "Citerius development flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
          };
        };
        pybibget_pkg = pkgs.python312Packages.buildPythonPackage rec {
          pname = "pybibget";
          version = "0.1.0";

          src = pkgs.fetchPypi {
            inherit pname version;
            hash = "sha256-M6CIctTOVn7kIPmsoHQmYl2wQaUzfel7ryw/3ebQitg=";
          };
          propagatedBuildInputs = with pkgs.python312Packages; [ 
            lxml
            httpx
            appdirs
            aiolimiter
            pybtex
            pylatexenc
            numpy
            networkx
            requests
          ]; 
        };
        python = pkgs.python312Packages.python;
        pythonEnv = python.withPackages (ps: with ps; [
          pandas
          numpy
          pyfzf
          arxiv
          readchar
          rich
          gitpython
          pybtex
          pybibget_pkg
        ]);
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            pybibget
          ];
        };
      }
    );
}
