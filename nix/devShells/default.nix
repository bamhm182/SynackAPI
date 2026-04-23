{ lib, pkgs, ... }:
let
  python = pkgs.python3.withPackages (ps: with ps; [
    # Runtime dependencies (from setup.py)
    alembic
    netaddr
    pathlib2
    psycopg2
    pyaml
    pycryptodome
    pyotp
    requests
    sqlalchemy
    urllib3

    # Dev dependencies
    coverage
    flake8
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python
  ];
  shellHook = ''
    current_dir="$PWD"
    while [ "$current_dir" != "/" ]; do
      if [ -e "$current_dir/flake.nix" ]; then
        export PROJECT_DIR="$current_dir"
        break
      fi
      current_dir=$(dirname "$current_dir")
    done

    echo "Python Version    : $(python3 --version)"
    echo "Project Directory : ''${PROJECT_DIR}"
  '';
}
