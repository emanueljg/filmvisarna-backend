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
          buildPythonPackage
          flask
          pymysql
        ; 
      in buildPythonPackage {
        inherit name;
        propagatedBuildInputs = [ flask pymysql ];
        src = ./.;
      };

    in {
      packages.default = pkg;
      packages.${name} = pkg;
    }) // (let name = "filmvisarna"; in { 
    # now we add on non-system-specific stuff

      # add module
      nixosModules = let 
        admin-user = "${name}-admin";
        api-user = "${name}-api";
        users = [ admin-user api-user ];
      in {
        default = self.nixosModules.${name}; 
        ${name} = (
          { config, pkgs, lib, ... }: with lib; let 
            cfg = config.services.${name}; 
            pkg = self.packages.${pkgs.system}.default;
          in {
            options.services.${name} = {
              enable = mkEnableOption self.description;
              
              dirPath = mkOption {
                type = types.str;
                default = "/var/lib/filmvisarna-backend";
                description = lib.mdDoc ''
                  Path to run the flask server in. 

                  This is necessary since the WSGI web server (gunicorn) 
                  needs to be run in the same directory as the flask module.
                '';
              };
            };

            config = let 
              inherit (lib.attrsets) genAttrs;
            in mkIf cfg.enable {

              # blegh..
              security.acme.acceptTerms = true;
              security.acme.defaults.email = "emanueljohnsongodin@gmail.com";
              
              services.nginx = {
                enable = true;
                virtualHosts."emanueljg.com" = {
                  forceSSL = true;
                  enableACME = true;
                  root = cfg.dirPath;
                  locations."/" = {
                    proxyPass = "http://127.0.0.1:8000";
                    recommendedProxySettings = true;
                    extraConfig = ''
                      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                      proxy_set_header X-Forwarded-Proto $scheme;
                      proxy_set_header X-Forwarded-Host $host;
                      proxy_set_header X-Forwarded-Prefix /;
                    '';
                  };
                };
              };

              networking.firewall.allowedTCPPorts = [ 443 ];
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

              systemd.tmpfiles.rules = [ 
                "d '${cfg.dirPath}' 0750 ejg users -" 
                ("L+ '${cfg.dirPath}/filmvisarna-backend.py'"
                 + " - - - - ${pkg}/bin/.filmvisarna-backend.py-wrapped")
              ];

              systemd.services."${name}-flask" = let
                gunicorn = pkgs.python3Packages.gunicorn;
              in {
                wantedBy = [ "multi-user.target" ];
                after = [ "network.target" ];
                path = [ gunicorn ];
                serviceConfig = {
                  User = "ejg";
                  Group = "users";
                  Type = "simple";
                  WorkingDirectory = cfg.dirPath;
                  ExecStart=''
                    ${gunicorn}/bin/gunicorn \
                      -w 4 \
                      --chdir ${cfg.dirPath} \
                      'filmvisarna-backend:app'
                  '';
                };
              };
            };
          }
        );
      };  # nixosModules
    })
  ;
}

