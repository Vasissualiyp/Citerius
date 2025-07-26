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
        ads = pkgs.python311Packages.buildPythonPackage rec {
          pname = "ads";
          version = "0.12.7";
    	  src = pkgs.fetchFromGitHub {
  		    owner = "andycasey";
  		    repo = "ads";
  		    rev = "6aa0e854a1f3dc1dcd242a36426ad5855b2cbcfe";
  		    hash = "sha256-lGfCyDCxRfLmzzAXpAJtxczWK1/UdEC7096JRBiKEcs=";
  		  };
          propagatedBuildInputs = with pkgs.python311Packages; [ six requests werkzeug mock ];
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
		  ads
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
