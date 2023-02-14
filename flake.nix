{
  description = "A cinema backend using Flask + MySQL";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs =  { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem(system: let

      name = "filmvisarna-backend";

      pkgs = import nixpkgs { inherit system; };

      pkg = let
        inherit (pkgs.python3Packages)
          buildPythonApplication
          flask
          pymysql
        ; 
      in buildPythonApplication {
        pname = name;
        version = "0.1";
        propagatedBuildInputs = [ flask pymysql ];
        src = ./.;
      };

    in {
      packages.default = pkg;
      packages.${name} = pkg;

      apps.default = {
        type = "app";
        program = "${self.packages.${system}.default}/bin/${name}.py";
      };
    }) // (let name = "filmvisarna"; in { 
    # now we add on non-system-specific stuff

      # add module
      nixosModules = let 
        pkg = self.packages."x86_64-linux".default;
        admin-user = "${name}-admin";
        api-user = "${name}-api";
        users = [ admin-user api-user ];
      in {
        default = self.nixosModules.${name}; 
        ${name} = (
          { config, pkgs, lib, ... }: with lib; let 
            cfg = config.services.${name}; in {

            options.services.${name} = {
              enable = mkEnableOption self.description;
            };

            config = let 
              inherit (lib.attrsets) genAttrs;
            in mkIf cfg.enable {
              networking.firewall.allowedTCPPorts = [ 5000 ];
              # since we are using unix socket auth,
              # we need to add corresponding OS users.
              users.users = genAttrs users (
                user: { 
                  isNormalUser = true;
                  group = user; 
                }
              );
              users.groups = genAttrs users (user: { });

              services.mysql = {
                enable = true;
                package = pkgs.mysql80;
                ensureDatabases = [ name ];
                ensureUsers = [
                  {
                    name = admin-user;
                    ensurePermissions."${name}.*" =
                      "ALL PRIVILEGES";
                  }
                  {
                    name = api-user;
                    ensurePermissions."${name}.*" = 
                      "SELECT, INSERT, UPDATE, DELETE";
                  }
                  {
                    name = "ejg";
                    ensurePermissions."${name}.*" =
                      "ALL PRIVILEGES";
                  }
                ];
              };

              systemd.services."${name}-flask" = let
                gunicorn = pkgs.python3Packages.gunicorn;
              in {
                after = [ "network.target" ];
                path = [ pkg gunicorn pkgs.coreutils ];
                wantedBy = [ "multi-user.target" ];
                serviceConfig = let
                  wd = "/var/lib/filmvisarna-backend";
                in {
                  User = "ejg";
                  Group = "users";
                  Type = "simple";
                  ExecStartPre="${pkgs.coreutils}/bin/ln -sf ${pkg}/bin/filmvisarna-backend.py ${wd}/filmvisarna-backend.py";
                  ExecStart="${gunicorn}/bin/gunicorn -w 4 'filmvisarna-backend:app'";
                  WorkingDirectory = wd;
                };
              };
            };
          }
        );
      };  # nixosModules
    })
  ;
}

