{ pkgs ? import <nixpkgs> {} }: let
  pypkgs = pkgs.python3Packages;
in pkgs.mkShell {
  name = "kolibrios.org";

  buildInputs = with pypkgs; [
    python
    virtualenv
    pkgs.nodePackages.sass
  ];

  shellHook = ''
    if [ ! -d "venv" ]; then
      python -m venv .venv
    fi

    source .venv/bin/activate

    if [ -f "requirements.txt" ]; then
      pip install -r requirements.txt
    fi
  '';
}
