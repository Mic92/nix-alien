from pathlib import Path
from unittest.mock import patch

from nix_alien import nix_ld


@patch("nix_alien.nix_ld.find_libs")
def test_create_nix_ld(mock_find_libs):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        nix_ld.create_nix_ld_drv("xyz")
        == """\
{ pkgs ? import <nixpkgs> { } }:

let
  inherit (pkgs) lib stdenv;
  NIX_LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
    bar.out
    foo.out
    quux.out
  ];
  NIX_LD = lib.fileContents "${stdenv.cc}/nix-support/dynamic-linker";
in
pkgs.writeShellScriptBin "xyz" ''
  export NIX_LD_LIBRARY_PATH='${NIX_LD_LIBRARY_PATH}'${"\\${NIX_LD_LIBRARY_PATH:+':'}$NIX_LD_LIBRARY_PATH"}
  export NIX_LD='${NIX_LD}'${"\\${NIX_LD:+':'}$NIX_LD"}
  "%s/xyz" "$@"
''
"""
        % Path(__file__).parent.parent.absolute()
    )


@patch("nix_alien.nix_ld.subprocess")
@patch("nix_alien.nix_ld.find_libs")
def test_main_wo_args(mock_find_libs, mock_subprocess, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    nix_ld.main(["xyz"])
    shell_nix = next((tmp_path / ".cache/nix-alien").glob("*/nix-ld/default.nix"))

    assert shell_nix.is_file()
    assert mock_subprocess.run.call_count == 2


@patch("nix_alien.nix_ld.subprocess")
@patch("nix_alien.nix_ld.find_libs")
def test_main_with_args(mock_find_libs, mock_subprocess, tmp_path):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }

    nix_ld.main(["--destination", str(tmp_path), "--recreate", "xyz", "--foo", "bar"])
    shell_nix = tmp_path / "default.nix"

    assert shell_nix.is_file()
    assert mock_subprocess.run.call_count == 2
