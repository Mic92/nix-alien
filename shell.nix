{ pkgs ? (import ./compat.nix).pkgs
, poetry2nix ? (import ./compat.nix).poetry2nix
}:

let
  appEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    python = pkgs.python39;

    editablePackageSources = {
      nix-alien = ./nix-alien;
      tests = ./tests;
    };

    overrides = poetry2nix.overrides.withDefaults (
      final: prev: {
        # Fix conflict between icontract and pylddwrap files
        icontract = prev.icontract.overrideAttrs (oldAttrs: {
          postInstall = (oldAttrs.postInstall or "") + ''
            rm -f $out/*.rst $out/*.txt
          '';
        });
      }
    );
  };
in
appEnv.env.overrideAttrs (oldAttrs: {
  buildInputs = with pkgs; [
    findutils
    fzf
    glibc.bin
    gnumake
    nix-index
    nixUnstable
    nixpkgs-fmt
    poetry
  ];
})
