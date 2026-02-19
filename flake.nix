{
  description = "Python development environment with uv for fast package management";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            python313Packages.python-lsp-server
            uv  # Fast Python package installer and resolver
            
            # Build dependencies that might be needed
            gcc
            zlib
            openssl
            libffi
            pkg-config
          ];
          
          shellHook = ''
            # Create virtual environment with uv if it doesn't exist
            if [ ! -d ".venv" ]; then
              echo "Creating virtual environment with uv..."
              uv venv
            fi
            
            # Activate virtual environment
            source .venv/bin/activate
            
            # Install requirements if requirements.txt exists
            if [ -f "requirements.txt" ]; then
              echo "Installing requirements from requirements.txt with uv..."
              uv pip install -r requirements.txt
            fi
            
            echo "Python environment with uv activated"
            echo "Python: $(python --version)"
            echo "UV: $(uv --version)"
            echo "Virtual environment: $VIRTUAL_ENV"
            echo ""
            echo "Usage:"
            echo "  Install package: uv pip install <package>"
            echo "  Install from requirements: uv pip install -r requirements.txt"
            echo "  Install dev dependencies: uv pip install -e ."
            echo "  Add package: uv add <package>"
            echo "  Sync dependencies: uv pip sync requirements.txt"
            echo ""
            echo "uv is significantly faster than pip for package installation!"
          '';
        };
      });
}
