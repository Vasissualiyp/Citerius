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
		python = pkgs.python312Packages; # Set python version

        pybibget_pkg = python.buildPythonPackage rec {
          pname = "pybibget";
          version = "0.1.0";

          src = pkgs.fetchPypi {
            inherit pname version;
            hash = "sha256-M6CIctTOVn7kIPmsoHQmYl2wQaUzfel7ryw/3ebQitg=";
          };
          propagatedBuildInputs = with python; [ 
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
        ads = python.buildPythonPackage rec {
          pname = "ads";
          version = "0.12.7";
    	  src = pkgs.fetchFromGitHub {
  		    owner = "andycasey";
  		    repo = "ads";
  		    rev = "6aa0e854a1f3dc1dcd242a36426ad5855b2cbcfe";
  		    hash = "sha256-lGfCyDCxRfLmzzAXpAJtxczWK1/UdEC7096JRBiKEcs=";
  		  };
          propagatedBuildInputs = with python; [ 
		    six 
			requests 
			werkzeug 
			mock 
			httpretty
		  ];
        };
        qspider = python.buildPythonPackage rec {
          pname = "qspider";
          version = "0.1.6";
    	  src = pkgs.python312Packages.fetchPypi {
            inherit pname;
            inherit version;
            hash = "sha256-kjBie3dmEbPfP9EPaG68/qEKcq/J+MPeQWkCpDpKH1U=";
          };
		  format = "other";
          propagatedBuildInputs = with python; [ 
		    termcolor
		    requests
		    colorama
		  ];
        };
        doi2pdf = python.buildPythonPackage rec {
          pname = "doi2pdf";
          version = "0.12.7";
    	  src = pkgs.fetchFromGitHub {
            owner = "0xFORK";
            repo = "doi2pdf";
            rev = "925b9b495025a344c8aa984f1f95d0afeadde72a";
            hash = "sha256-PuAGFmQngoBBQFMWdvgzdAmfnngz90mjeHgX984Ujmc=";
          };
          propagatedBuildInputs = with python; [ 
		    termcolor
			qspider
			requests
			pillow
			beautifulsoup4
		  ];
        };
        pythonEnv = python.python.withPackages (ps: with ps; [
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
		  #doi2pdf
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
