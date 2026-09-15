{
  description = "SynackAPI";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }@inputs:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs { inherit system; config.allowUnfree = true; };
      lib = pkgs.lib;
    in {
      devShells = {
        default = import ./nix/devShells/default.nix { inherit lib pkgs; };
      };
    });
}
