# Changelog

## [1.7.2](https://github.com/Strandgaard96/mc-gamertime/compare/v1.7.1...v1.7.2) (2026-08-28)


### Bug Fixes

* **web:** correct the product name in link previews and the PWA manifest ([11982fa](https://github.com/Strandgaard96/mc-gamertime/commit/11982fa09e6bc2840fdd368ebd82a552a5156460))
* **web:** use one spelling of "favourite" on the player profile ([316d6e6](https://github.com/Strandgaard96/mc-gamertime/commit/316d6e63694656cb09c40f233beaf89938c98736))

## [1.7.1](https://github.com/Strandgaard96/mc-gamertime/compare/v1.7.0...v1.7.1) (2026-08-21)


### Bug Fixes

* **api:** tell caches not to store API responses ([9862c42](https://github.com/Strandgaard96/mc-gamertime/commit/9862c42fde25f4e8acb8e0277e08cb45a900b61a))
* **auth:** account lockout 500'd on the cloud deployment ([892c001](https://github.com/Strandgaard96/mc-gamertime/commit/892c001df20ce45aff7f66b288277ed1cfef9e36))
* **auth:** guard the unknown-user timing hash against over-long passwords too ([6737cba](https://github.com/Strandgaard96/mc-gamertime/commit/6737cbabfa347dbd3557a00eedacba09a9f34849))
* **auth:** reject passwords over bcrypt's 72-byte limit instead of 500ing ([f603d5c](https://github.com/Strandgaard96/mc-gamertime/commit/f603d5cfb522984f1f6fc53416f3702c2cb1343c))
* **auth:** set the session cookie's Secure flag from the request scheme ([835076e](https://github.com/Strandgaard96/mc-gamertime/commit/835076ee6b9c1912237ef7e53a87b96dcd554328))
* **cloud:** require a session to read avatars and uploaded images ([5cc2d8f](https://github.com/Strandgaard96/mc-gamertime/commit/5cc2d8fa7b6c3165944eaf9c7342193ec1366507))
* **infra:** stop CloudFront serving DynamoDB exports from the web bucket ([3066e76](https://github.com/Strandgaard96/mc-gamertime/commit/3066e767492ae24991c56b8b8c12954fbae3fc79))


### Performance Improvements

* **media:** reuse images for 20 minutes, with cache-busted avatar URLs ([f8aef93](https://github.com/Strandgaard96/mc-gamertime/commit/f8aef938b19b5fea36397c3af59d8a80d5c803d2))

## [1.7.0](https://github.com/Strandgaard96/mc-gamertime/compare/v1.6.0...v1.7.0) (2026-08-20)


### Features

* make self-hosting the default deployment, AWS opt-in ([3f16bd9](https://github.com/Strandgaard96/mc-gamertime/commit/3f16bd9a6fe971fad62d01f8fc1a87b79aa48f03))


### Bug Fixes

* **cors:** allow the CloudFront distribution domain as a browser origin ([61d2928](https://github.com/Strandgaard96/mc-gamertime/commit/61d2928375174fca50c9308f4985c8b01349405f))
* **deps:** patch HIGH-severity CVEs in api and docs-site ([9854a18](https://github.com/Strandgaard96/mc-gamertime/commit/9854a1817474e453684972159931af271435b4c4))
* **docker:** apply Debian security updates in the image build ([8105c10](https://github.com/Strandgaard96/mc-gamertime/commit/8105c10b31c816e7d92d85d9ba0fb304f5c6f5e2))
* **scripts:** list-users crashed on users created through the web UI ([27b13cb](https://github.com/Strandgaard96/mc-gamertime/commit/27b13cbb143b07602d3238843feda3506a6562ff))

## [1.6.0](https://github.com/Strandgaard96/mc-gamertime/compare/v1.5.0...v1.6.0) (2026-07-04)


### Features

* fail at startup when no users exist and admin vars unset ([eefbd72](https://github.com/Strandgaard96/mc-gamertime/commit/eefbd729d5cb7c2cd1140015a3f863bfe5a57d65))
* fail at startup when no users exist and admin vars unset ([c27ccd4](https://github.com/Strandgaard96/mc-gamertime/commit/c27ccd4e0dad7b558814d773d90fa341fa664a33))


### Bug Fixes

* auth security hardening — password bounds, bcrypt rounds, cookie attributes ([c5a0120](https://github.com/Strandgaard96/mc-gamertime/commit/c5a01202b2e45eab6721c5467b764978cd618505))
* cap password field length at 1024 chars to prevent bcrypt DoS ([2d873bd](https://github.com/Strandgaard96/mc-gamertime/commit/2d873bd490d4090160be38279956f55cfb9da69b))
* make bcrypt work factor explicit (rounds=12); document rate-limiter Lambda scope ([09ec388](https://github.com/Strandgaard96/mc-gamertime/commit/09ec3889a907c9f60b6c4999c4d56eaedae705d9))
* match delete_cookie attributes to set_cookie (secure, samesite=strict) ([8ec3e6e](https://github.com/Strandgaard96/mc-gamertime/commit/8ec3e6effbd3c84981ed371cbc1d03c4090d9dc8))
* raise minimum password length to 12 characters (NIST 800-63B) ([4596c56](https://github.com/Strandgaard96/mc-gamertime/commit/4596c56b2004accdaae0cbe17996815b7e0f1d68))
* repair CI — stale bootstrap tests + docs Node version ([238e0d7](https://github.com/Strandgaard96/mc-gamertime/commit/238e0d779700b2bd79090390f38c94a2f99708c0))
* **security:** API & infrastructure hardening from audit ([1b4824c](https://github.com/Strandgaard96/mc-gamertime/commit/1b4824c3f1b72828fe524d6f6ff67c66b85c4055))
* **security:** authorization audit findings ([83477ce](https://github.com/Strandgaard96/mc-gamertime/commit/83477ce9ec68601f687b12de8060934983079ff5))
* **security:** logging & monitoring audit findings ([85c7eaf](https://github.com/Strandgaard96/mc-gamertime/commit/85c7eafcd51c60988715b4294d898daaaf0bb4ef))
* **security:** session role re-check from cookie audit (S-2) ([7e6314b](https://github.com/Strandgaard96/mc-gamertime/commit/7e6314be75881f71478283e53f5a6d339f11a025))
* use explicit bcrypt rounds=12 in admin bootstrap path ([a56a49e](https://github.com/Strandgaard96/mc-gamertime/commit/a56a49ecc06599889f77fc07e4f99f6e1a4c0070))

## [1.5.0](https://github.com/Strandgaard96/mc-gamertime/compare/v1.4.1...v1.5.0) (2026-06-25)


### Features

* add appBaseUrl to AdminSettings type and API client ([88b4bdb](https://github.com/Strandgaard96/mc-gamertime/commit/88b4bdba7af99ac1d6a6172cf754246bab98538d))
* add DB-backed appBaseUrl setting ([c3b37e1](https://github.com/Strandgaard96/mc-gamertime/commit/c3b37e1a639595a51b99a39434c0dde20de68d38))
* add Instance URL card to Settings page ([76bd06f](https://github.com/Strandgaard96/mc-gamertime/commit/76bd06fbfe6cfc5076b9c0913bbe6dab1eef9f76))
* implement appBaseUrl validator (scheme required, trailing-slash stripped, empty clears) ([6bf29f8](https://github.com/Strandgaard96/mc-gamertime/commit/6bf29f868b279a9cef9c14718f8ced26d46d3701))
* prefer DB appBaseUrl over env var for reset-link host ([1d96656](https://github.com/Strandgaard96/mc-gamertime/commit/1d96656b9b0b0cf07272fcc6a9e2079fa7d5d4c7))


### Bug Fixes

* correct bgg_token setup instructions in AWS deploy guide ([4493ff1](https://github.com/Strandgaard96/mc-gamertime/commit/4493ff1ec9a94b5d206587a1e44c03df8bc56784))
* document Instance URL setting, reject scheme-only appBaseUrl ([f988f9d](https://github.com/Strandgaard96/mc-gamertime/commit/f988f9dab09304f82ff5766e5424d6919340ac56))
* selfhost security hardening (reset-link spoofing + rate-limit collapse) ([80045fe](https://github.com/Strandgaard96/mc-gamertime/commit/80045fef24a463212765564b1b55719f712864f8))
* sqlite_import.py accepts export-tables.py's boardsite-prefixed filenames ([f8f7d16](https://github.com/Strandgaard96/mc-gamertime/commit/f8f7d16a51cddf896e505ba82a10d25fca189044))
* trust forwarded client IP from private ranges so rate limiting survives a reverse proxy ([3d046e8](https://github.com/Strandgaard96/mc-gamertime/commit/3d046e84db69ed13f56b0bcc9126ccc181f836e0))

## [1.4.1](https://github.com/Strandgaard96/mc-gamertime/compare/v1.4.0...v1.4.1) (2026-06-21)


### Bug Fixes

* gate GHCR push on a Trivy scan inside publish.yml ([4d91b70](https://github.com/Strandgaard96/mc-gamertime/commit/4d91b7001ecbbeb0f0858aa4ad9479ef36438c11))
* gate GHCR push on a Trivy scan inside publish.yml ([154b819](https://github.com/Strandgaard96/mc-gamertime/commit/154b819fd27b81489e9f38d032f5afb4547e125d))

## [1.4.0](https://github.com/Strandgaard96/mc-gamertime/compare/v1.3.0...v1.4.0) (2026-06-21)


### Features

* add local trivy dependency scan to pre-commit ([bc5ff5d](https://github.com/Strandgaard96/mc-gamertime/commit/bc5ff5d82629a21cc9d22bcc7fa5cdb8bb4bfec1))
* add local trivy dependency scan to pre-commit ([944f1f2](https://github.com/Strandgaard96/mc-gamertime/commit/944f1f2cf11118ea69c8bd78d11c0eb66dc5530e))


### Bug Fixes

* patch starlette and cryptography CVEs flagged by Trivy ([78d6a98](https://github.com/Strandgaard96/mc-gamertime/commit/78d6a983c09dd776ea68e2d60a19e31e6d5bf196))
* patch starlette and cryptography CVEs flagged by Trivy image scan ([6962368](https://github.com/Strandgaard96/mc-gamertime/commit/6962368ae7ee90d8d922221f7099c4a2c7caad0d))

## [1.3.0](https://github.com/Strandgaard96/mc-gamertime/compare/v1.2.0...v1.3.0) (2026-06-21)


### Features

* add frontend test infra and CI image vulnerability scanning ([096c9b1](https://github.com/Strandgaard96/mc-gamertime/commit/096c9b1e1aedbb83206be378114e3da5ef6ebb16))
* add game image upload API call and shared upload hook ([635450e](https://github.com/Strandgaard96/mc-gamertime/commit/635450e785a624d54741704fff8109be74006832))
* add manual game entry mode to AddGameDialog ([512b27d](https://github.com/Strandgaard96/mc-gamertime/commit/512b27d3b03e38594f50f19adfa07034aa7e1ddd))
* add POST /api/games/upload for game cover images ([6ed4b14](https://github.com/Strandgaard96/mc-gamertime/commit/6ed4b14a572ae6a528de80f1639c921a9701d687))
* allow editing core game fields (name, image, players, etc.) for any game ([76b616c](https://github.com/Strandgaard96/mc-gamertime/commit/76b616ce0a6f4b0433b9331b161619dbc8019006))


### Bug Fixes

* allow clearing core game fields in the edit dialog ([83641e1](https://github.com/Strandgaard96/mc-gamertime/commit/83641e128d3b24925d4f6e34c288919b4ed2857e))
* allow game-images/ prefix in the selfhost storage proxy ([fd662dd](https://github.com/Strandgaard96/mc-gamertime/commit/fd662dd85af515a0063f2cb77dd6b9a323a4a50a))
* correct trivy-action tag (needs v prefix, bump to latest) ([df7038a](https://github.com/Strandgaard96/mc-gamertime/commit/df7038ac7692abe06ec29106d5dcc7f0b93f8f0b))
* origin guard fails open when ORIGIN_TOKEN is unset ([80b1143](https://github.com/Strandgaard96/mc-gamertime/commit/80b1143b8e3760e5936940dcaa913ddf02d91289))
* origin guard fails open when ORIGIN_TOKEN unset ([edbe2ec](https://github.com/Strandgaard96/mc-gamertime/commit/edbe2ec2012ae0c0fa29f873de32ae40d2918aac))
* pin vitest to stable 3.x to fix npm ci in CI ([b7051fb](https://github.com/Strandgaard96/mc-gamertime/commit/b7051fbf381ed4ec1251b5b321d3e801d6601d7d))
* reset manual-entry image state when AddGameDialog closes ([8a28420](https://github.com/Strandgaard96/mc-gamertime/commit/8a28420b493240c92848d11375cedaefbaee2451))

## [1.2.0](https://github.com/Strandgaard96/mc-gamertime/compare/v1.1.0...v1.2.0) (2026-06-21)


### Features

* add automated backup script for selfhost with retention ([348652b](https://github.com/Strandgaard96/mc-gamertime/commit/348652ba5dd2ff311b7d8429e51d34efd2040b27))
* add forgot/reset-password pages and document SMTP config ([19e4440](https://github.com/Strandgaard96/mc-gamertime/commit/19e4440f3b2dadf52fd027b382b1f87598f9340d))
* add forgot/reset-password routes and --email flag to user scripts ([3f7442a](https://github.com/Strandgaard96/mc-gamertime/commit/3f7442a913da4550db634db084c4fabaf8248511))
* add gated /metrics endpoint behind METRICS_ENABLED ([420c768](https://github.com/Strandgaard96/mc-gamertime/commit/420c768e051f992dab39551f2fbfccc421c30c1c))
* add GET/PUT settings API routes ([a2b700a](https://github.com/Strandgaard96/mc-gamertime/commit/a2b700ab2b9a9303269a46dd272043501630f11f))
* add interactive first-run wizard to create-user.py ([3f0cc54](https://github.com/Strandgaard96/mc-gamertime/commit/3f0cc54364a32dad5543e015c6342fceecb6c6d3))
* add password-reset token signing to lib/auth.py ([417eb41](https://github.com/Strandgaard96/mc-gamertime/commit/417eb419d828ba5044942c52ce2e8c9d3fb2cfdb))
* add prometheus_client metrics counters ([3978ffe](https://github.com/Strandgaard96/mc-gamertime/commit/3978ffe0b634e8c39e740334048b49630c01d8eb))
* add settings API client functions and types ([f8e8282](https://github.com/Strandgaard96/mc-gamertime/commit/f8e828234881d81711436b6b166b18ba0c692a9a))
* add settings table for instance-level config ([5517c46](https://github.com/Strandgaard96/mc-gamertime/commit/5517c46ed2a7a45c134efe26dec20772a484357b))
* add SettingsPage and usePublicSettings hook ([b86b83e](https://github.com/Strandgaard96/mc-gamertime/commit/b86b83ebd507f37481937c04249d91d95dff211f))
* add SQLite schema migration framework ([513f5ce](https://github.com/Strandgaard96/mc-gamertime/commit/513f5ce9af939ec757619ecf82dae2d4a78dc488))
* add sqlite_export.py for selfhost table-level JSON export ([3acd79f](https://github.com/Strandgaard96/mc-gamertime/commit/3acd79f78ffe06c1957f864c9b0a4dc789eaf73c))
* add sqlite_import.py with atomic validation for selfhost data import ([f2b3d5f](https://github.com/Strandgaard96/mc-gamertime/commit/f2b3d5f92c0b206da54e43a8512867084041cd12))
* add stdlib SMTP mailer for selfhost password reset ([8e1c12c](https://github.com/Strandgaard96/mc-gamertime/commit/8e1c12c0474856028efdd630d17c5e103dd7e151))
* **api:** bootstrap self-host admin user from ADMIN_USERNAME/ADMIN_PASSWORD ([310add0](https://github.com/Strandgaard96/mc-gamertime/commit/310add07176bc33fdc9dbbd96558fb690f5b230f))
* layer DB-backed BGG token override over env/SSM fallback ([0c6ff5a](https://github.com/Strandgaard96/mc-gamertime/commit/0c6ff5ad28a5e432d0d2122b30d59b51814f74a7))
* make docker-compose.yml self-sufficient for selfhost ([c5b05be](https://github.com/Strandgaard96/mc-gamertime/commit/c5b05be32ab08b0a44f45fa958d28757edcc9b7c))
* move settings entry point from nav tab to header cog icon ([911757d](https://github.com/Strandgaard96/mc-gamertime/commit/911757de0b50358ff4f52842aee35b0b406eb8b7))
* provision settings DynamoDB table in Terraform ([a90bb4b](https://github.com/Strandgaard96/mc-gamertime/commit/a90bb4b7876326c42356ac212a88f464beb7412c))
* resolve BGG token through DB-override precedence at cold start ([b9301fd](https://github.com/Strandgaard96/mc-gamertime/commit/b9301fdc18b89bd144194934251b989acbcb3894))
* self-host default admin bootstrap via ADMIN_USERNAME/ADMIN_PASSWORD ([534c88a](https://github.com/Strandgaard96/mc-gamertime/commit/534c88a1b5948c7ffebc7ceedf2df233341526de))
* self-host P3 — password reset, metrics endpoint, interactive wizard ([a7b0ffa](https://github.com/Strandgaard96/mc-gamertime/commit/a7b0ffa44ee33eaeba7db54b210893e0e9dd4df5))
* selfhost P0 data safety (backup automation, sqlite export/import) ([cb67de2](https://github.com/Strandgaard96/mc-gamertime/commit/cb67de251b6df7ce8ad80f96537c1827dadee6a8))
* selfhost P2 maintainability (SQLite migrations, commit convention, recovery runbook) ([82c520e](https://github.com/Strandgaard96/mc-gamertime/commit/82c520ebe83445d36caaa35f8af66d644e254bc6))
* split settings page into independent branding and integrations cards ([82ae9a0](https://github.com/Strandgaard96/mc-gamertime/commit/82ae9a0349c8cf0c59519cc461bc862050b5765e))
* wire Settings page into nav and replace hardcoded brand strings ([a15bcde](https://github.com/Strandgaard96/mc-gamertime/commit/a15bcde1226aaeec74e9d1a6a15c8f5a98adf0b7))


### Bug Fixes

* **docs:** correct stale code refs and broken prose in docs-site ([6b2165a](https://github.com/Strandgaard96/mc-gamertime/commit/6b2165a6e5f49bbd9c5dc3083c53a2aad9e07045))
* install sqlite3 CLI in runtime image for disaster-recovery runbook ([603a329](https://github.com/Strandgaard96/mc-gamertime/commit/603a329e181307e726fddd8d6494bddfda9204c6))
* narrow sqlite_export OperationalError handling to missing-table only ([ec293b2](https://github.com/Strandgaard96/mc-gamertime/commit/ec293b261141914f7d24ac413ad7b33f7b4f49b9))
* rate-limit /reset-password to match /forgot-password ([b71b618](https://github.com/Strandgaard96/mc-gamertime/commit/b71b618e0c2b3154b847d2ed9506a17509e3344b))
* show explanatory message on ResetPasswordPage when token is missing ([af8f9f0](https://github.com/Strandgaard96/mc-gamertime/commit/af8f9f036695d1bd7a25eef24451d00416f7e883))
* stop deriving password-reset link host from client-supplied Host header ([249444b](https://github.com/Strandgaard96/mc-gamertime/commit/249444bd8cf76ee8981fe10c6cf0375d3997fda5))
* warn before live-DB export/import, verify backup tar contents ([4f91623](https://github.com/Strandgaard96/mc-gamertime/commit/4f9162393a96ddff18bc3cf3da64f297e7c5a04f))

## [1.1.0](https://github.com/Strandgaard96/mc-gamertime/compare/v1.0.2...v1.1.0) (2026-06-19)


### Features

* add DynamoTable semantic update methods (add_to_set, remove_from_set, increment_with_timestamp) ([972104a](https://github.com/Strandgaard96/mc-gamertime/commit/972104a470769b9f0eb44da776919720cbfa34a7))
* add LocalFsClient for selfhost STORAGE_BACKEND=local ([69deb99](https://github.com/Strandgaard96/mc-gamertime/commit/69deb99cb91406c8dfb1c6b3bef604c7d00f6b6b))
* add SQLite-backed table implementation for selfhost DB_BACKEND=sqlite ([5f1f30f](https://github.com/Strandgaard96/mc-gamertime/commit/5f1f30fe4cef0090336a421e2bd3b6ed7957b4be))
* collapse selfhost docker-compose to a single app container (SQLite + local fs) ([d50be09](https://github.com/Strandgaard96/mc-gamertime/commit/d50be097a5903c7814216f2bd6b7d428e35f67ca))
* dispatch to LocalFsClient when STORAGE_BACKEND=local ([3d42ea1](https://github.com/Strandgaard96/mc-gamertime/commit/3d42ea1b0474180e9f94efd0b6c90109b9235214))
* dispatch to SQLite backend when DB_BACKEND=sqlite ([aabc29a](https://github.com/Strandgaard96/mc-gamertime/commit/aabc29ac7a559d531a7ff3a920ede935f8638fed))
* register /storage router when STORAGE_BACKEND=local ([b92ca00](https://github.com/Strandgaard96/mc-gamertime/commit/b92ca0082f38e5789a12f7990ce555fb1b1b1c13))
* support STORAGE_BACKEND=local in upload-URL and storage-proxy 404 handling ([7f331b2](https://github.com/Strandgaard96/mc-gamertime/commit/7f331b2605307dab2c078f363c6435d7fcb487ef))


### Bug Fixes

* **docs:** add missing PUID/PGID to .env.example template ([3fe5938](https://github.com/Strandgaard96/mc-gamertime/commit/3fe593842522b08238ad73508f9ffcac43c81206))
* **docs:** port Backups and migration content into Backups & Upgrades page ([31c9ac4](https://github.com/Strandgaard96/mc-gamertime/commit/31c9ac446d3e6d3e493daf656b7ea7ac3087d908))
* **docs:** remove leftover TODO placeholder from Features page ([eed0707](https://github.com/Strandgaard96/mc-gamertime/commit/eed0707b3ec30c070ff416d686bf103fad3c06d3))
* **docs:** replace stale volume check with bind-mount permission check ([fa7f0e8](https://github.com/Strandgaard96/mc-gamertime/commit/fa7f0e8ac6d7251d2312a97b2a591515b9514953))
* **docs:** restore all three archives in backups example, not just dynamodb ([d360eda](https://github.com/Strandgaard96/mc-gamertime/commit/d360edaa98faa0b105b4f5293327033db990e33f))
* **docs:** sync configuration page JWT_SECRET path to config/ bind mount ([513cb30](https://github.com/Strandgaard96/mc-gamertime/commit/513cb30e94ad83bf12ae53d3e35ab921f81f5a2b))
* **docs:** sync HTTPS page certificate storage path to config/ bind mount ([5720563](https://github.com/Strandgaard96/mc-gamertime/commit/572056349793f180d6a8dd28fb61646c898ef4a3))
* **docs:** unbreak MDX build, sync architecture page to config/ bind mounts ([d8871e5](https://github.com/Strandgaard96/mc-gamertime/commit/d8871e5a8026acc0e3dfa7d989d16cf1fc79573f))
* reject path traversal in LocalFsClient keys ([9e7ddd9](https://github.com/Strandgaard96/mc-gamertime/commit/9e7ddd9065ab954f5b6bc26f0c477a19a52e8a19))

## [1.0.2](https://github.com/Strandgaard96/mc-gamertime/compare/v1.0.1...v1.0.2) (2026-06-16)


### Bug Fixes

* fix url migration ([809a8d3](https://github.com/Strandgaard96/mc-gamertime/commit/809a8d3052c06c3a2b4f65dc14baaa5dd837826a))

## [1.0.1](https://github.com/Strandgaard96/mc-gamertime/compare/v1.0.0...v1.0.1) (2026-06-16)


### Bug Fixes

* formatting and update pre-commit ([7b39524](https://github.com/Strandgaard96/mc-gamertime/commit/7b395243db8353d9655e5f8791f0b96aa35f8869))
* prevent query of players endpoint on homepage when not logged in ([91aadfb](https://github.com/Strandgaard96/mc-gamertime/commit/91aadfb17970aa531f193dc24aec48fbc0d673ce))

## 1.0.0 (2026-06-16)


### Features

* 12 UX/UI improvements across frontend ([deb6a20](https://github.com/Strandgaard96/mc-gamertime/commit/deb6a205937d3bf1880d8db71a3eedbe8d1ecc15))
* add 5 dark themes to registry, remove parchment ([7e6b511](https://github.com/Strandgaard96/mc-gamertime/commit/7e6b5117cb87aa287b8f975ecaceed844209ec15))
* add achievement computation library with tests ([8e5da5c](https://github.com/Strandgaard96/mc-gamertime/commit/8e5da5c85d667f1ea76934b88dbcfa949b0b91c9))
* add Achievement, PlayerStats, GameStat types and getPlayerStats API function ([53e5461](https://github.com/Strandgaard96/mc-gamertime/commit/53e5461e1406ee55fe46c6151c6a57aa97e36a61))
* add AchievementBadge component ([a1154f0](https://github.com/Strandgaard96/mc-gamertime/commit/a1154f0bfce2b847674bad1cf7e601b32c78cfb0))
* add achievements, win rate trend chart, and per-game stats to player profiles ([915b2e6](https://github.com/Strandgaard96/mc-gamertime/commit/915b2e6c991421f459265c23d98b099a8d20424b))
* add backend API documentation to handbook ([1878d9f](https://github.com/Strandgaard96/mc-gamertime/commit/1878d9f6cadc4e00c899679d264753fc469d8f0d))
* add By Game expandable section to Leaderboard page ([7e445fc](https://github.com/Strandgaard96/mc-gamertime/commit/7e445fc61b3af029182f70d49482940f07136922))
* add CSS variable blocks for 5 new dark themes, remove parchment ([5bf60e9](https://github.com/Strandgaard96/mc-gamertime/commit/5bf60e9c1fe4d5ccee2157475176d6509562c5d1))
* add DELETE /api/results/{pk} endpoint (admin only) ([4253863](https://github.com/Strandgaard96/mc-gamertime/commit/4253863a30b57470515ca0bb7af42c68422866bc))
* add DELETE /api/users/{username} with self/last-admin guards ([57af473](https://github.com/Strandgaard96/mc-gamertime/commit/57af4730edb8d594aad78e143325245cbb2c8585))
* add delete_user DB helper ([93f4a72](https://github.com/Strandgaard96/mc-gamertime/commit/93f4a72e2f62332f3bb16a695039147fa0a606c7))
* add deleteResult API fn and useDeleteResult hook ([20676ad](https://github.com/Strandgaard96/mc-gamertime/commit/20676add11c20ac3cfd4d4f6efbd0a33be9227fa))
* add dice SVG favicon ([df92106](https://github.com/Strandgaard96/mc-gamertime/commit/df92106db7351c7eb6bce48976ce4f85a54a1e62))
* add edit-user dialog to UsersPage (display name, role, password) ([afc0043](https://github.com/Strandgaard96/mc-gamertime/commit/afc0043fd43156de4f9ecdd4b0c235caa132d0b7))
* add escalating-delay brute-force protection to login ([14fe1bf](https://github.com/Strandgaard96/mc-gamertime/commit/14fe1bfe28e8ad33eec2709e01d61346266b9491))
* add favorites-only toggle to CatalogFilters ([f026faf](https://github.com/Strandgaard96/mc-gamertime/commit/f026faf0383c65126df3b2b7a5d913c62723e27a))
* add field validators to recommended route (non-empty gamePk and blurb) ([fec1699](https://github.com/Strandgaard96/mc-gamertime/commit/fec169993ca5ff14dd91c134eea14d8414d03bfb))
* add field validators to results route (non-empty, date format, score &gt;= 0) ([db6a559](https://github.com/Strandgaard96/mc-gamertime/commit/db6a5595e98bb4bf490642b338ab08335e7f8fbe))
* add frontend documentation to handbook ([a2aebd1](https://github.com/Strandgaard96/mc-gamertime/commit/a2aebd1919c7d449b805ee3d06f3717f5612e5aa))
* add gameStats breakdown to compute_stats ([df84a99](https://github.com/Strandgaard96/mc-gamertime/commit/df84a990d7a09bbe9c483b6282e5654b644e4344))
* add GET /players/{id}/stats with achievements, per-game stats, win rate trend ([2a87630](https://github.com/Strandgaard96/mc-gamertime/commit/2a87630f13d649a142b7e14c335452bc43ead708))
* add infrastructure documentation to handbook ([50bf40a](https://github.com/Strandgaard96/mc-gamertime/commit/50bf40ae7ddc5a1a3045b008e8f9deee3297edce))
* add initial handbook structure and DynamoDB documentation ([718c389](https://github.com/Strandgaard96/mc-gamertime/commit/718c389c6a266226f7d068057f623e9064368cb2))
* add inline delete confirm and post link buttons to game log ([cfc4b9a](https://github.com/Strandgaard96/mc-gamertime/commit/cfc4b9ae4a364ececc4c37d030f79d79748018a2))
* add lib/db package with per-entity DynamoDB modules ([1ebc44e](https://github.com/Strandgaard96/mc-gamertime/commit/1ebc44e9c5ffd1ecacf00495bb94bf808c61ac92))
* add optional score field to log result dialog and display in session history ([e57dcb5](https://github.com/Strandgaard96/mc-gamertime/commit/e57dcb5ac8cd534b709b55d08d80cf7f79f43147))
* add pressable tap-feedback utility, apply to Button ([af5d96f](https://github.com/Strandgaard96/mc-gamertime/commit/af5d96f5dc82c56b69c3554408c0741f2f3b5321))
* add PUT /users/:username admin route for display-name/role/password updates ([bf8279a](https://github.com/Strandgaard96/mc-gamertime/commit/bf8279a82e241f3702ad4b76af52ee2297b7f4ae))
* add rec detail endpoint, hasPost, BGG metadata denormalization, content field ([0d6d426](https://github.com/Strandgaard96/mc-gamertime/commit/0d6d42650bdf9eef380aa39a1550a42fc7413b97))
* add RecDetailPage with BGG metadata, rich content, and public access ([199dafe](https://github.com/Strandgaard96/mc-gamertime/commit/199dafe1561719a7f591a50525661571dd028b0a))
* add RecEditorPage — full-screen Tiptap editor for rec posts ([e94dfa5](https://github.com/Strandgaard96/mc-gamertime/commit/e94dfa5f3168d2a212d886387fbe39079926cd35))
* add RecommendationDetail type, getRecommendedDetail API, useRecommendedDetail hook ([d32da44](https://github.com/Strandgaard96/mc-gamertime/commit/d32da44e637f655ac7f10e57b83f40c607c4b9dc))
* add slug to rec URLs (e.g. /recommended/catan) ([410ca7d](https://github.com/Strandgaard96/mc-gamertime/commit/410ca7dd8a9958ed3d9be3c6ec20ef0e0374ccf6))
* add subtitle to recommendations section on landing page ([0c47a30](https://github.com/Strandgaard96/mc-gamertime/commit/0c47a300ffdf27ce480945975f5034fa1aeab357))
* add subtle feature strip to landing page ([77d6d47](https://github.com/Strandgaard96/mc-gamertime/commit/77d6d4794c99f8c7d45b18435fcfdd9acdf59d7a))
* add tap feedback to game cards, post cards, game list rows ([3a4535f](https://github.com/Strandgaard96/mc-gamertime/commit/3a4535f9abc69ae752d2029cb5bf54a701e81561))
* add tap feedback to mobile bottom nav tabs ([b6b2328](https://github.com/Strandgaard96/mc-gamertime/commit/b6b23280da31d9023409278d304487cb77fa721f))
* add tokenVersion claim for JWT session revocation ([a4f1cb4](https://github.com/Strandgaard96/mc-gamertime/commit/a4f1cb4e5553ae663dd380a73ab811c9eea33b27))
* add updateUser API function ([408501f](https://github.com/Strandgaard96/mc-gamertime/commit/408501f701f5d6a912645a81d4320884fe9e9dc2))
* add useDraft localStorage hook for post draft recovery ([25ca62c](https://github.com/Strandgaard96/mc-gamertime/commit/25ca62ce0c5f8982c0a5ac6ff04ea87518efb178))
* add usePlayerStats hook ([12521f4](https://github.com/Strandgaard96/mc-gamertime/commit/12521f493448c1e696a5aaea0a34495e5b074ebd))
* add user deletion to UsersPage UI ([d6b9f86](https://github.com/Strandgaard96/mc-gamertime/commit/d6b9f8609a14de923347ec19a68202d94828a342))
* add WinRateTrendChart component using Recharts ([7babc66](https://github.com/Strandgaard96/mc-gamertime/commit/7babc6640503ab65f1c79fdfd21bb06dad3a0887))
* admin result editing via PUT /api/results/{id} ([141be01](https://github.com/Strandgaard96/mc-gamertime/commit/141be012aaebf7f6f81ad89131a86cecae66e844))
* animated empty state for game catalog ([0d80d4f](https://github.com/Strandgaard96/mc-gamertime/commit/0d80d4f2f813dc74dceb3b90d3355d2e41396759))
* **api:** add /storage proxy for selfhost S3-compatible stores ([92e4e74](https://github.com/Strandgaard96/mc-gamertime/commit/92e4e74abf78cf86bf9c76af6a7f7088be73d099))
* **api:** add comment create/delete endpoints ([f8a4d39](https://github.com/Strandgaard96/mc-gamertime/commit/f8a4d39b963f19cc39dd745ecf0c3e7463b51ce0))
* **api:** add Elo rating computation ([05260a6](https://github.com/Strandgaard96/mc-gamertime/commit/05260a66ef185b9123b785dc6774b2837a93aeb9))
* **api:** add IP rate limiting (5/min) to POST /api/auth/login ([4c1c64b](https://github.com/Strandgaard96/mc-gamertime/commit/4c1c64b168063b224c1889e2a2a3433d01f31407))
* **api:** add make_s3_client() factory for selfhost S3-compatible stores ([0c220fc](https://github.com/Strandgaard96/mc-gamertime/commit/0c220fc49021f5ee54cc506cbfa3015be2695213))
* **api:** add milestone detection to result POST response ([3335915](https://github.com/Strandgaard96/mc-gamertime/commit/3335915470a18db85a90e7cbd41b5c6bd61b3592))
* **api:** add notifications DynamoDB table and db layer ([1267c80](https://github.com/Strandgaard96/mc-gamertime/commit/1267c80bd9bcdbf3df2dac970a2fac5e84197ce5))
* **api:** add notifications list/read endpoints ([1d541b2](https://github.com/Strandgaard96/mc-gamertime/commit/1d541b2af9825d5963f88edfca58f62d7baf9083))
* **api:** add ORIGIN_GUARD_ENABLED flag for selfhost (no CloudFront) ([ae6f034](https://github.com/Strandgaard96/mc-gamertime/commit/ae6f0348472bd8965cb226f06aa0b0585ae10db6))
* **api:** add per-game player variable config + game edit endpoint ([deca2a8](https://github.com/Strandgaard96/mc-gamertime/commit/deca2a88b825841ed25b5b66622964dbda203457))
* **api:** add POST /api/reactions/toggle ([84979c4](https://github.com/Strandgaard96/mc-gamertime/commit/84979c446576aa3b5d2a8c60e31f4af67c3c1533))
* **api:** add PUBLIC_RECOMMENDED_ENABLED flag for selfhost ([2d5bff5](https://github.com/Strandgaard96/mc-gamertime/commit/2d5bff5df353fc69f482eefbe678380d5e96ca10))
* **api:** add Pydantic request model to games route ([6bb6907](https://github.com/Strandgaard96/mc-gamertime/commit/6bb6907c8ba297288d8cd4375082cd7e64f51ab9))
* **api:** add Pydantic request model to users route ([9681e46](https://github.com/Strandgaard96/mc-gamertime/commit/9681e4634020f93c57d59ea621156406c8285a3a))
* **api:** add Pydantic request models to auth and players routes ([ab9e157](https://github.com/Strandgaard96/mc-gamertime/commit/ab9e15711faf737008fb3907d5552dd25b91a313))
* **api:** add Pydantic request models to posts route ([8a5a692](https://github.com/Strandgaard96/mc-gamertime/commit/8a5a692b4de8458a9f20b2280fbde0c7e17c759f))
* **api:** add Pydantic request models to recommended route ([5fb0317](https://github.com/Strandgaard96/mc-gamertime/commit/5fb031718e5603e7bc2a0cbe604497a00b35ed1f))
* **api:** add Pydantic request models to results route ([8ab8855](https://github.com/Strandgaard96/mc-gamertime/commit/8ab8855bbb018e385228229e767733a8ec783638))
* **api:** add reactions table and GET /api/reactions ([1431bfa](https://github.com/Strandgaard96/mc-gamertime/commit/1431bfa10fb3c9d79a53ac58fe65fa8a02d8ddcb))
* **api:** add recommended games CRUD with public GET endpoint ([6b67285](https://github.com/Strandgaard96/mc-gamertime/commit/6b67285fc6c92263638f0b6e84e1ec2107389c1d))
* **api:** add SECRETS_PROVIDER=env for selfhost secret config ([059e7af](https://github.com/Strandgaard96/mc-gamertime/commit/059e7afa2d5609f7d33d232730294ff515441013))
* **api:** compute per-variable and per-seat win/pick rate stats ([7416821](https://github.com/Strandgaard96/mc-gamertime/commit/7416821fc6f849595a33422231b14f97ee0a646b))
* **api:** detect and notify newly-earned achievements on result creation ([6c6cf66](https://github.com/Strandgaard96/mc-gamertime/commit/6c6cf660864a21fb359ad634c9655e6708dea5f6))
* **api:** make achievements declarative via composable rules ([2796d13](https://github.com/Strandgaard96/mc-gamertime/commit/2796d13f1d23dabe44370ab6fa714f6a455b1248))
* **api:** rank leaderboard by Elo rating ([84d002d](https://github.com/Strandgaard96/mc-gamertime/commit/84d002d5300c1b863896a667cada31b4d12e1067))
* **api:** serve SPA via STATIC_DIR and register /storage proxy for selfhost ([f76b37e](https://github.com/Strandgaard96/mc-gamertime/commit/f76b37ea215fb9f149026c9b60eab92a99ad0129))
* **api:** support DYNAMODB_ENDPOINT_URL for selfhost dynamodb-local ([8a60ebe](https://github.com/Strandgaard96/mc-gamertime/commit/8a60ebe7b5d650e1637a7490b3e9e7262f8af7a0))
* **api:** validate per-player variables and seat order against game config ([b719a17](https://github.com/Strandgaard96/mc-gamertime/commit/b719a1751b4207bf3a233df3f11ff4a8158ef965))
* **api:** validate player IDs and winnerId membership on result creation ([9e8401c](https://github.com/Strandgaard96/mc-gamertime/commit/9e8401cb7acb6e0d849658810fac7babf516bd6a))
* **api:** wire slowapi limiter into FastAPI app ([f29fb5e](https://github.com/Strandgaard96/mc-gamertime/commit/f29fb5e8d69d330f10a9cb0f9722a540bffc5ea0))
* autosave blog post drafts to localStorage with restore banner ([456e648](https://github.com/Strandgaard96/mc-gamertime/commit/456e648df7014362796aa302c82a5507bd101a81))
* block deletion of users referenced in results, clean up avatar ([1e863ee](https://github.com/Strandgaard96/mc-gamertime/commit/1e863ee78da30e308a85c03f5354959d3a811d59))
* bump tokenVersion on logout, add revoke-sessions ops script ([b8ab399](https://github.com/Strandgaard96/mc-gamertime/commit/b8ab399b7888839cb3933566ca256b2a4a3113e7))
* dashboard home page, sidebar nav, leaderboard podium ([8a240df](https://github.com/Strandgaard96/mc-gamertime/commit/8a240df678b163fd5fa247cee63ae4132f1c7b87))
* delete lib/dynamo.py; clean up conftest to use FakeTable only ([a9b5c97](https://github.com/Strandgaard96/mc-gamertime/commit/a9b5c97ebcac0272b6d1854e53de3e895dc60249))
* detect and toast new achievements after logging a game result ([0719c4e](https://github.com/Strandgaard96/mc-gamertime/commit/0719c4ed28bae4c0dad2d9ef55ab6544bd98cf2f))
* **docker:** add .env.example for selfhost S3 credentials ([0af2848](https://github.com/Strandgaard96/mc-gamertime/commit/0af2848d278eda19f754a8faa87c4e5331771932))
* **docker:** add Caddy reverse-proxy overlay for HTTPS (Tailscale/public/LAN) ([3aa62b9](https://github.com/Strandgaard96/mc-gamertime/commit/3aa62b9fbeb156b52cb0f8744874c2fb7e8063f9))
* **docker:** add docker-compose.yml for selfhost stack (app + dynamodb-local + seaweedfs) ([d5b4f51](https://github.com/Strandgaard96/mc-gamertime/commit/d5b4f51f1221c75170e68a63259e66a632cb21f1))
* **docker:** add multi-stage selfhost Dockerfile (web build + api runtime) ([1dd2da1](https://github.com/Strandgaard96/mc-gamertime/commit/1dd2da1815e52986273231fbca474f3e69379de0))
* **docker:** add SeaweedFS S3 identity config template (single identity, no anonymous) ([9cde9a8](https://github.com/Strandgaard96/mc-gamertime/commit/9cde9a83ca1c1524c217da765a9e81a901037ce1))
* **docker:** add selfhost entrypoint (JWT secret + table/bucket bootstrap) ([aedc47c](https://github.com/Strandgaard96/mc-gamertime/commit/aedc47c8cb4200cb3d13b889efbf842a74dfdb19))
* **docker:** add setup.sh to generate .env and render SeaweedFS config ([1c1cd2b](https://github.com/Strandgaard96/mc-gamertime/commit/1c1cd2b006beb56a885aed1c9795f24e41c36c3f))
* **docs:** add architecture page with container diagram and volumes table ([36ecba0](https://github.com/Strandgaard96/mc-gamertime/commit/36ecba07f802d2940a81e2162f66050e35404ddc))
* **docs:** add cloud deploy and contributing sections ([037c291](https://github.com/Strandgaard96/mc-gamertime/commit/037c2913fddb2b07fd5bbd433824d64e42d32ecd))
* **docs:** add Features card to landing page ([418f472](https://github.com/Strandgaard96/mc-gamertime/commit/418f4728ad0b17be82d4b5231fa821b79416ebb0))
* **docs:** add features page ([4f9e623](https://github.com/Strandgaard96/mc-gamertime/commit/4f9e623a88577a71a4625706bcec0e449a7b1a68))
* **docs:** add landing page and self-hosting section ([81fa6ed](https://github.com/Strandgaard96/mc-gamertime/commit/81fa6ed2f1e61348ca9d6152cf5fc730aa8ec68e))
* **docs:** add sidebar ordering and GHCR quickstart tip ([6a419c0](https://github.com/Strandgaard96/mc-gamertime/commit/6a419c0fbeef4544435c8728d9514d0364622ebd))
* **docs:** add site URL, sitemap, and Mermaid CDN ([b94ad88](https://github.com/Strandgaard96/mc-gamertime/commit/b94ad88b3f06c9f6e46748c85b99a8aa44a77979))
* **docs:** scaffold Astro Starlight docs-site ([b7235fe](https://github.com/Strandgaard96/mc-gamertime/commit/b7235fea457d63f12357d540db6d2a927643b0ea))
* edit button and mood display on session cards ([1c688de](https://github.com/Strandgaard96/mc-gamertime/commit/1c688de717510f45872d8fb9f13bbeaacbd1807a))
* editorial featured card layout for RecommendedPage ([26ac0b4](https://github.com/Strandgaard96/mc-gamertime/commit/26ac0b4554afd11bb4c8c72aa926d2d1c3ec03b1))
* editorial sidebar and pull-quote blurb for RecDetailPage ([abdc4be](https://github.com/Strandgaard96/mc-gamertime/commit/abdc4be7a673f48130ba780b7ed9fb807c648174))
* emoji picker in post editor toolbar ([362ef1d](https://github.com/Strandgaard96/mc-gamertime/commit/362ef1dc1af253cdf03ea063657681983be9be1e))
* enable DynamoDB PITR and deletion protection on all tables ([9bd4a2f](https://github.com/Strandgaard96/mc-gamertime/commit/9bd4a2f627e125d1fb3073abcfd09e114e02ee0b))
* enable S3 versioning and 90-day lifecycle on blog images ([467f1be](https://github.com/Strandgaard96/mc-gamertime/commit/467f1beb9fbc26bc12ecbbbe5e41832293cbe8ed))
* fix idFromPk for clean IDs, update Player type, remove addPlayer ([b166a21](https://github.com/Strandgaard96/mc-gamertime/commit/b166a216fd7ab3d876d0fdee0e1ab9cdfb15fa6b))
* health endpoint + backend-down detection at login ([4b9ff6a](https://github.com/Strandgaard96/mc-gamertime/commit/4b9ff6a237420a152923825905996dbe8daf2cfe))
* hero header card for PlayerProfilePage ([4aaf889](https://github.com/Strandgaard96/mc-gamertime/commit/4aaf88996851c01adeda84e5b03d79c800f0bfb6))
* implement public landing page with hero and game teaser ([feaf109](https://github.com/Strandgaard96/mc-gamertime/commit/feaf109519b57e14e19a7b7a9f0f131e18485dcb))
* **infra:** add boardsite-reactions DynamoDB table ([3fc7917](https://github.com/Strandgaard96/mc-gamertime/commit/3fc7917b102910baa2d05e5e3fc673f1ec5fc459))
* **infra:** add IP-allowlist WAF for dev CloudFront distribution ([8eda0e9](https://github.com/Strandgaard96/mc-gamertime/commit/8eda0e9244987206d5912b8b087ce78320702f9e))
* make rec cards clickable when hasPost, add Write/Edit Post buttons to admin ([b1cbfb1](https://github.com/Strandgaard96/mc-gamertime/commit/b1cbfb16de7912365456aad8219ad531fd1fc7b4))
* manual DynamoDB table export script ([e480ad5](https://github.com/Strandgaard96/mc-gamertime/commit/e480ad503d32a6df6d712e577455cfbb7113e046))
* migrate routes/auth to lib.db.users ([3d47f49](https://github.com/Strandgaard96/mc-gamertime/commit/3d47f49201fcc3926735c942b3bd9436740ab029))
* migrate routes/games to lib.db.games; clean pk (no GAME# prefix) ([3d9efc8](https://github.com/Strandgaard96/mc-gamertime/commit/3d9efc8731aa92e76acc26cf1a3df224b61d7b26))
* migrate routes/players; remove create_player; list returns public user info ([9bb13cf](https://github.com/Strandgaard96/mc-gamertime/commit/9bb13cf9e8449dcb64764724762be79920a44ea5))
* migrate routes/posts to lib.db.posts; clean pk (no POST# prefix) ([b1effc5](https://github.com/Strandgaard96/mc-gamertime/commit/b1effc5b675cc540384227ccb878a497612a10c3))
* migrate routes/recommended to lib.db.recs + lib.db.games; clean pk ([549ea67](https://github.com/Strandgaard96/mc-gamertime/commit/549ea677d14186bf2fd180250574be2e15824910))
* migrate routes/results to lib.db; validate players via lib.db.users; clean pk ([87689c8](https://github.com/Strandgaard96/mc-gamertime/commit/87689c8bdfb7fffd9fe858be3e7b8afb8a8b97c2))
* migrate routes/stats to lib.db.results ([21dd5e2](https://github.com/Strandgaard96/mc-gamertime/commit/21dd5e257e49e07896b0aa6117961f6fba675c8e))
* migrate routes/users to lib.db.users; clean item shape ([2f0894c](https://github.com/Strandgaard96/mc-gamertime/commit/2f0894c49cd894645a94ffdbb457a8b63b9789c9))
* mood selector and edit mode in LogResultDialog ([1f37ce5](https://github.com/Strandgaard96/mc-gamertime/commit/1f37ce58addef0729bcccc80b2753bfa59cec3f2))
* optional mood (1-5) on results ([65aaa98](https://github.com/Strandgaard96/mc-gamertime/commit/65aaa986b8fe025ee713f6b30f6d75e77ba5e98a))
* per-game average/high score stats and best-score badge ([3f3cfa8](https://github.com/Strandgaard96/mc-gamertime/commit/3f3cfa8b9162d252b7ff9c65750ba5174ac8b68d))
* per-player average score trend chart ([909f217](https://github.com/Strandgaard96/mc-gamertime/commit/909f2171012b789a3b582b75493c8a381ea4ca9a))
* Perfect 10 score achievement ([a7ab80d](https://github.com/Strandgaard96/mc-gamertime/commit/a7ab80dd699cfaca20741aa4f20c6bb8d8ef90a5))
* pre-select session in post editor from ?session URL param ([ed470bf](https://github.com/Strandgaard96/mc-gamertime/commit/ed470bfa19e7597c16568e908b8d4fbb6bbc61b7))
* publish Docker image to GHCR on push to main and version tags ([078d9b4](https://github.com/Strandgaard96/mc-gamertime/commit/078d9b43ff1726e451ac0e10d49146326fd3a781))
* remove per-player score from log card avatar row ([1a7fcc2](https://github.com/Strandgaard96/mc-gamertime/commit/1a7fcc2331699748e6d68c89ade2ece4430e36df))
* route / to LandingPage for unauthenticated users ([cd0c43c](https://github.com/Strandgaard96/mc-gamertime/commit/cd0c43c83dfdffda09c3d1e464a7dce09a2fa175))
* **scripts:** add create-user.py to bootstrap users in DynamoDB ([6fd6d71](https://github.com/Strandgaard96/mc-gamertime/commit/6fd6d7123042aac335916f946d646b7b42409237))
* **scripts:** add delete-user.py to remove users from DynamoDB ([d7a0b04](https://github.com/Strandgaard96/mc-gamertime/commit/d7a0b04f58456a1bd4ac8107871c9d5f9048774f))
* **scripts:** add idempotent DynamoDB Local table bootstrap for selfhost ([cc7ceca](https://github.com/Strandgaard96/mc-gamertime/commit/cc7cecadf21080b3d09be04b67dff65012c48c15))
* **scripts:** add idempotent S3 bucket bootstrap for selfhost ([dd1f874](https://github.com/Strandgaard96/mc-gamertime/commit/dd1f8746e36fbb77841d9114516cda6539294d14))
* **scripts:** respect DYNAMODB_ENDPOINT_URL in user-management scripts ([0784dbe](https://github.com/Strandgaard96/mc-gamertime/commit/0784dbec4b4e2b15b34eb9a459bcdf2024abd57e))
* self-host Space Grotesk via [@fontsource](https://github.com/fontsource) — remove Google Fonts CDN ([61fdb47](https://github.com/Strandgaard96/mc-gamertime/commit/61fdb47d29b8fffc6a6397b853f0087a7eac7283))
* **selfhost:** replace caddy named volumes with config/ bind mounts ([45b26df](https://github.com/Strandgaard96/mc-gamertime/commit/45b26dfa71241a3fd4d9edbe3ea88fc741d3fe9c))
* **selfhost:** replace named volumes with config/ bind mounts ([8631fb3](https://github.com/Strandgaard96/mc-gamertime/commit/8631fb3c16b6d3b502c3806413b337219e96940b))
* show session-expired toast and redirect back after re-login ([54c7643](https://github.com/Strandgaard96/mc-gamertime/commit/54c7643338326ae7efba498aceb5cb186df9606f))
* skip Lambda build when api/ source unchanged ([668ced7](https://github.com/Strandgaard96/mc-gamertime/commit/668ced732a5d5a2f9df215d17e6a0f484a3786c6))
* styled numbered rank badges in LeaderboardTable ([b558d43](https://github.com/Strandgaard96/mc-gamertime/commit/b558d43bb984ccd0402a08b78a05b22c0a84ecf9))
* update landing page hero subtitle copy ([a246d5d](https://github.com/Strandgaard96/mc-gamertime/commit/a246d5ddc4315e098935da688c880dce938bf813))
* validate game existence when creating result ([c15d75d](https://github.com/Strandgaard96/mc-gamertime/commit/c15d75d179beef59608845f6e08154858faa5635))
* **web:** add admin dialog to configure per-game player variables and turn order ([c3e128f](https://github.com/Strandgaard96/mc-gamertime/commit/c3e128f055e6bda8023b217ea3fa9bd91489f8d9))
* **web:** add AdminRecommendedPage with CRUD management and routing ([f70692f](https://github.com/Strandgaard96/mc-gamertime/commit/f70692f36789a3b0dca90f8d2fad2854b7f16fba))
* **web:** add asChild prop to Button for rendering as a single link element ([45a0a66](https://github.com/Strandgaard96/mc-gamertime/commit/45a0a66bd4f0b023e2cdba1ddde53b5ae478e6ca))
* **web:** add Avatar component with deterministic initials colors ([5cab5f0](https://github.com/Strandgaard96/mc-gamertime/commit/5cab5f03e9684dce18baa5783ed5588c56ee9a78))
* **web:** add Avatar, Lucide stat icons, and font-display to detail pages ([8cc65a9](https://github.com/Strandgaard96/mc-gamertime/commit/8cc65a97b4b651515eac755b2ef589d7c3bdb929))
* **web:** add ChevronLeft back icon and font-display to post pages ([1539caa](https://github.com/Strandgaard96/mc-gamertime/commit/1539caa2600c7c29d2ae3a2da31b42c6f73feaf6))
* **web:** add Lucide icons, font-display headings, and empty state polish to pages ([3d8aa42](https://github.com/Strandgaard96/mc-gamertime/commit/3d8aa420779e8cb08e9e48beb917986ccfcbb272))
* **web:** add Lucide icons, hover effects, and image gradient to game cards ([84b4d60](https://github.com/Strandgaard96/mc-gamertime/commit/84b4d608aff780a6e5db0e88a40c8d6558d78cdc))
* **web:** add MC GameTime branding, theme picker, Lucide nav icons, Sonner toaster ([90882b2](https://github.com/Strandgaard96/mc-gamertime/commit/90882b2aeb12be19db639127972d77c911984ed6))
* **web:** add medals, win rate bars, avatars, and streak flames to leaderboard ([e970080](https://github.com/Strandgaard96/mc-gamertime/commit/e97008044dfc10152e52293d867d5d3d18ead40e))
* **web:** add notification bell to header nav ([2f734b2](https://github.com/Strandgaard96/mc-gamertime/commit/2f734b23c9f85c84c284789dd83c14d84b3eabdc))
* **web:** add notifications API client and hook ([91a75a5](https://github.com/Strandgaard96/mc-gamertime/commit/91a75a597bdb258d32a07f3b8b81e9d68bbf78c6))
* **web:** add page slide transitions via Framer Motion AnimatePresence ([b75a76f](https://github.com/Strandgaard96/mc-gamertime/commit/b75a76fe3e78857c6da105116d9ff34f420c8736))
* **web:** add PageTransition component and install framer-motion + canvas-confetti ([2eed98d](https://github.com/Strandgaard96/mc-gamertime/commit/2eed98dc2676f2d3305beb2d91abf98873aeffef))
* **web:** add Player Wrapped recap to profile page ([4e9af8e](https://github.com/Strandgaard96/mc-gamertime/commit/4e9af8e509fc14e9fbf4f141e99cd18fc5feadf3))
* **web:** add public /recommended landing page with game cards ([af618f4](https://github.com/Strandgaard96/mc-gamertime/commit/af618f45bc4a0fe66875ee5e1d535c0f883f1f59))
* **web:** add PWA icon assets and generation script ([d258c27](https://github.com/Strandgaard96/mc-gamertime/commit/d258c273b6ce24ccefefe68afa3a6ed7a77c78e4))
* **web:** add PWA manifest, service worker, and iOS meta tags ([31ad6e1](https://github.com/Strandgaard96/mc-gamertime/commit/31ad6e146a219534eddbff42e1e7d2d7ba6604b0))
* **web:** add reactions and comments to session cards ([b9e9923](https://github.com/Strandgaard96/mc-gamertime/commit/b9e9923dd07325fc59832d29256cc7b289e2ce1a))
* **web:** add reactions/comments API client and hooks ([8c6ded8](https://github.com/Strandgaard96/mc-gamertime/commit/8c6ded8826ccc8bdfb9d62417a22f0b6749aef1f))
* **web:** add Recommendation type, API functions, and useRecommended hook ([f93e86a](https://github.com/Strandgaard96/mc-gamertime/commit/f93e86a51bb9dd5df8d28c30d4250839d4bb677f))
* **web:** add stagger animations, win rate bars, and stat counters ([fabf02a](https://github.com/Strandgaard96/mc-gamertime/commit/fabf02aae15ae705d018208008ad4fe61241d518))
* **web:** add theme system, dark-gold/midnight palettes, Space Grotesk font ([3239388](https://github.com/Strandgaard96/mc-gamertime/commit/3239388643d1818e6440d0fd023deed1258698d9))
* **web:** add toast notifications to all mutation hooks ([86debf6](https://github.com/Strandgaard96/mc-gamertime/commit/86debf6bb976b813994ed32904642b391bd99029))
* **web:** add types for player variables, seat tracking, and variable/seat stats ([d132b3d](https://github.com/Strandgaard96/mc-gamertime/commit/d132b3d446b75eb3a9a1bc5e915d7071ec15d6af))
* **web:** add updateGame API client and useUpdateGame hook ([1c946eb](https://github.com/Strandgaard96/mc-gamertime/commit/1c946eb72c78d621c262cb6d4c78c83f3819a64f))
* **web:** add WrappedOverlay slideshow component ([44bb72d](https://github.com/Strandgaard96/mc-gamertime/commit/44bb72d7c251653d5ef4b4f26514a151e9f97311))
* **web:** collect player variables and seat order in LogResultDialog ([c652f8c](https://github.com/Strandgaard96/mc-gamertime/commit/c652f8cd155e822b20069b15c70b5093c83d62e1))
* **web:** confetti burst + milestone toast on game log ([9fa1cf6](https://github.com/Strandgaard96/mc-gamertime/commit/9fa1cf64cfb1f827974c30198265d02901a62d05))
* **web:** render achievement icons from the backend def ([c1d2618](https://github.com/Strandgaard96/mc-gamertime/commit/c1d26188e13c5c395525a59b4366e21d94a9e516))
* **web:** replace window.location.href auth redirects with navigation singleton ([7bbb549](https://github.com/Strandgaard96/mc-gamertime/commit/7bbb549618b55bd58fffb4943b0c726137067741))
* **web:** respect safe-area insets in standalone PWA mode ([4dff232](https://github.com/Strandgaard96/mc-gamertime/commit/4dff232e746f893c62df97112cc3947b9eba6e30))
* **web:** show Elo rating column on leaderboard ([4b5d529](https://github.com/Strandgaard96/mc-gamertime/commit/4b5d5298eef1a200fcc931f80012cf46a4663fa3))
* **web:** show per-variable and per-seat win/pick rates on game stat cards ([0ace10d](https://github.com/Strandgaard96/mc-gamertime/commit/0ace10de0c0e33413299c5226fd9bbc0633bdbf0))
* **web:** show update toast when new service worker is available ([14f8d4f](https://github.com/Strandgaard96/mc-gamertime/commit/14f8d4fda4858fb1cf736b86b542e7dc382893a7))
* **web:** sync theme-color meta to active theme ([1b0aded](https://github.com/Strandgaard96/mc-gamertime/commit/1b0aded3b212ca0457273306434580ee03c71d60))


### Bug Fixes

* 5 audit quick-wins — nav picks, upload toast, favorite await, list-view log button, game-detail log entry ([aa5ec6f](https://github.com/Strandgaard96/mc-gamertime/commit/aa5ec6f19aecc59df939e6d78819db085df15025))
* add 14-day noncurrent expiry for Vite assets and abort incomplete multipart uploads ([c12e1f2](https://github.com/Strandgaard96/mc-gamertime/commit/c12e1f2b4e079c64749c22e7c6c1d63fd1246d7a))
* add aria-hidden to decorative feature strip icons ([7c637b1](https://github.com/Strandgaard96/mc-gamertime/commit/7c637b13a389304174aa23d0bfa69eb5ed68a46f))
* Add auth fix for lambda startup ([1178536](https://github.com/Strandgaard96/mc-gamertime/commit/1178536931ef9a52c03594d8eabec08fefe63618))
* add blurb validator to UpdateRecommendedBody to prevent whitespace updates ([2df9b8a](https://github.com/Strandgaard96/mc-gamertime/commit/2df9b8a0fe3d0c16665bb54c06e11fd7627bf1cb))
* add CloudFront security response headers policy (HSTS, X-Frame-Options, X-Content-Type-Options) ([4dd03cd](https://github.com/Strandgaard96/mc-gamertime/commit/4dd03cd55711dd8244d23cf07adf4ca818625c78))
* add Features label above feature strip ([569d7ce](https://github.com/Strandgaard96/mc-gamertime/commit/569d7cec2f0c7120e628670fbe65cdc36a78b0b7))
* add missing defusedxml pin to requirements.txt (prod 500s on every route) ([db92796](https://github.com/Strandgaard96/mc-gamertime/commit/db927960879c0bc4dfcd5a181ac1ac77a38b2b5e))
* add paginated_scan helper; replace all unbounded scan() calls ([633de82](https://github.com/Strandgaard96/mc-gamertime/commit/633de82caaddaee4ef8d9817d8798da4fa5fc81e))
* add target and rel to external links in privacy policy ([8d55588](https://github.com/Strandgaard96/mc-gamertime/commit/8d55588f07aba353007d415288bd1556b1bbf7d8))
* add zero-guard to dominant achievement division ([d645250](https://github.com/Strandgaard96/mc-gamertime/commit/d6452501efae0ce54f4749678a8bbe51b4f10a25))
* address code review findings from UX improvement batch ([78544e2](https://github.com/Strandgaard96/mc-gamertime/commit/78544e2ae4ab47f0d771dd08921d86820cc440ed))
* allow clearing optional fields via explicit null in rec/post updates ([68c6c06](https://github.com/Strandgaard96/mc-gamertime/commit/68c6c06dff99ae90caae0d796b598709f185273c))
* allowlist content types on image upload endpoint ([33b08a6](https://github.com/Strandgaard96/mc-gamertime/commit/33b08a6d7e63a71edcdc0de226a128a082d661a2))
* **api:** apply prefix allowlist to /storage PUT (security review finding) ([43cb8da](https://github.com/Strandgaard96/mc-gamertime/commit/43cb8da973116009fa7831541f412615fc520a0e))
* **api:** centralize object base URL for selfhost display + upload URLs ([9b5fca0](https://github.com/Strandgaard96/mc-gamertime/commit/9b5fca00915268d325793e4ba6ad235a7d412584))
* **api:** generalize /storage PUT into an authenticated upload sink ([39ef3e3](https://github.com/Strandgaard96/mc-gamertime/commit/39ef3e372a292f510baaa218db40125362e06b88))
* **api:** replace deprecated datetime.utcnow() with datetime.now(timezone.utc) ([67cb5ae](https://github.com/Strandgaard96/mc-gamertime/commit/67cb5ae4dbd95f432071e8142fabb7d9d587baa7))
* **api:** strip favorites from game PUT response, normalize null playerVariables ([71e7aaa](https://github.com/Strandgaard96/mc-gamertime/commit/71e7aaaf60cac748055032bdf6697fc930036578))
* atomic failed-login counter increment ([f8d69d5](https://github.com/Strandgaard96/mc-gamertime/commit/f8d69d5983c0e181796795f9f9170a3aa13c71f8))
* avatar size cap, constant-time origin compare, pin upload extension ([3760d1a](https://github.com/Strandgaard96/mc-gamertime/commit/3760d1aa05e0432d289685059949f673809be9ed))
* build lambda.zip for Python 3.12 manylinux (fixes pydantic_core import error) ([aec2ac0](https://github.com/Strandgaard96/mc-gamertime/commit/aec2ac04200fb859d3caa39a5083dd1bf6c14311))
* bump tokenVersion on role/password update; reject empty displayName/password ([46adf08](https://github.com/Strandgaard96/mc-gamertime/commit/46adf08e7773ca20c98a11b99287a4ed22985394))
* constrain score input to range 1-10 ([9771e7f](https://github.com/Strandgaard96/mc-gamertime/commit/9771e7f576b21edc6e88ea9bcec4888db3f58c69))
* correct CloudFront response headers policy block names ([e59b697](https://github.com/Strandgaard96/mc-gamertime/commit/e59b697ab83e0a81027442011ed59104e50c653e))
* correct yearPublished camelCase label in CatalogFilters ([8e90eba](https://github.com/Strandgaard96/mc-gamertime/commit/8e90ebaf1967f2f9eae14ffeb28754e3a9dcf38c))
* define _floats_to_decimal in db/base.py; apply float conversion in put_post and put_rec ([6d6c603](https://github.com/Strandgaard96/mc-gamertime/commit/6d6c60365e7d99f690db04f7c0c114ec86a5063e))
* disable delete-user button while mutation pending ([574e24c](https://github.com/Strandgaard96/mc-gamertime/commit/574e24ce476979134f764184a60a7e0c72da1d52))
* **docker:** add .dockerignore, run as non-root, add healthcheck (code review findings) ([4d19592](https://github.com/Strandgaard96/mc-gamertime/commit/4d1959264181d0e20434edfe37c4983fb534eb88))
* **docker:** add resource limits and security hardening (no-new-privileges, cap_drop) ([b00e46a](https://github.com/Strandgaard96/mc-gamertime/commit/b00e46adcb506a9ba744c1dc97c144dc0c7e940e))
* **docker:** drop dynamodb-local root via init container that pre-chowns the volume ([8eb173f](https://github.com/Strandgaard96/mc-gamertime/commit/8eb173f98c6046724bdbe33dca73a0f83a0288ba))
* **docker:** fix healthcheck regressions — curl -s for dynamodb, nc for seaweedfs S3 port, revert image name ([7ff2943](https://github.com/Strandgaard96/mc-gamertime/commit/7ff2943f0a52b1f39adc951d6f62e6371850e995))
* **docker:** fix seaweedfs healthcheck false-positive, probe correct port, use canonical image name ([acb74c3](https://github.com/Strandgaard96/mc-gamertime/commit/acb74c3f91bf392c9afa64772179fd34c3205a2c))
* **docker:** pin image versions, add restart policies and healthcheck-based startup ordering ([e52f298](https://github.com/Strandgaard96/mc-gamertime/commit/e52f298302f17cd380d5c9a9677da2a62765a833))
* **docker:** publish port 8080 in caddy overlay for LAN default option ([80834b9](https://github.com/Strandgaard96/mc-gamertime/commit/80834b9aa200dfcd59bee6392402039c9bc6736d))
* **docker:** selfhost smoke-test fixes (dynamodb-local volume perms, SeaweedFS bucket creation via filer API) ([4269ff0](https://github.com/Strandgaard96/mc-gamertime/commit/4269ff0c69e03a76938f25473cf1bfed962b6d65))
* **docs:** clarify base vs optional Caddy container in architecture intro ([445bed9](https://github.com/Strandgaard96/mc-gamertime/commit/445bed9ee5f9afe68590906405a11121da494d9c))
* emoji picker popup collapses to 0-width grid columns ([5d1cb91](https://github.com/Strandgaard96/mc-gamertime/commit/5d1cb919aeed4f3a00a107345e69eba53ff4c432))
* enforce score 1-10 server-side, close milestone scan race ([26edf1c](https://github.com/Strandgaard96/mc-gamertime/commit/26edf1c511578d8ac56b3f6f5eb5e57d31404cc6))
* future-date slack for non-UTC users, block game delete with references ([2e5d654](https://github.com/Strandgaard96/mc-gamertime/commit/2e5d65469dc9e11153f4aeaffdba04e96fcc07a0))
* gate autosave on draftToRestore; skip restore for empty drafts ([c2d96e3](https://github.com/Strandgaard96/mc-gamertime/commit/c2d96e3df2d56f208d83cffe187124704fe31efa))
* gate GameCard PenLine button behind admin role check ([1709b23](https://github.com/Strandgaard96/mc-gamertime/commit/1709b23a962536b2efdd0e17020b35a9b2bf9268))
* guard self-demotion in edit-user dialog; toast on no-op submit ([b5c065d](https://github.com/Strandgaard96/mc-gamertime/commit/b5c065d2eee083c67cf6851d9f65718b805891be))
* guard winRate division in gameStats computation ([db395ec](https://github.com/Strandgaard96/mc-gamertime/commit/db395ec3cf3c1e17dd04ff90ea7ed05ed84a3d12))
* handle indented comments in requirements.txt parsing ([a4ab822](https://github.com/Strandgaard96/mc-gamertime/commit/a4ab82251a6ea1347b197440e5d7dec70923ca08))
* harden BGG client URL encoding and XML parsing ([ffc5124](https://github.com/Strandgaard96/mc-gamertime/commit/ffc5124c08efec7471b12d00d38456eee2de8ebf))
* increase web-assets lifecycle noncurrent expiry to 90 days to prevent blog image override ([9e85e78](https://github.com/Strandgaard96/mc-gamertime/commit/9e85e78fa33dc0427e325ed11ff8567b26c66ecf))
* **infra:** wire REACTIONS_TABLE env var into Lambda ([3e388b7](https://github.com/Strandgaard96/mc-gamertime/commit/3e388b74d586c959bd8f810abbed7a4362e11dfc))
* invalidate detail cache on recommendation update; invalidate playerStats on result delete ([a38bf18](https://github.com/Strandgaard96/mc-gamertime/commit/a38bf184a108c5aad428cf4fdda5c321392c266f))
* lock down game-creation schema against mass assignment ([04909c9](https://github.com/Strandgaard96/mc-gamertime/commit/04909c9ba5e32afc4b9acc2e2040091cfaaac976))
* low-impact UX polish ([d77b0d8](https://github.com/Strandgaard96/mc-gamertime/commit/d77b0d8e52922bd22808917d5c92a6cf2f9f226c))
* Make infrastructure domain independent on naming ([7dda327](https://github.com/Strandgaard96/mc-gamertime/commit/7dda3275f24f7fc65d8224feb8eaf37e480d866a))
* make Post.gamePk/sessionPk/gameName optional to match backend; guard PostCard crash ([b742f62](https://github.com/Strandgaard96/mc-gamertime/commit/b742f626e4abf929bd02f21515cfa7c56ad1f90b))
* polish and consistency across remaining pages ([5c7227c](https://github.com/Strandgaard96/mc-gamertime/commit/5c7227c40e6b5b4b0f6f962ee6a82aab6a62fbe4))
* reject negative scores client-side, document route-list invariant ([b408ba2](https://github.com/Strandgaard96/mc-gamertime/commit/b408ba29b133e894420fabbf2cbeb9cb872f676d))
* remove featured card treatment on RecommendedPage — all recs now uniform grid ([4d50abe](https://github.com/Strandgaard96/mc-gamertime/commit/4d50abe455da3f27f1c7ddaecd9bb772fbab2b14))
* remove gratuitous get_user guard from get_player_stats ([6de59df](https://github.com/Strandgaard96/mc-gamertime/commit/6de59df1211c58306fd41d0a824aba85ce67709e))
* remove models.py from build.sh (file no longer exists) ([77756f6](https://github.com/Strandgaard96/mc-gamertime/commit/77756f6e228899687dfaa136206e92bfbf6359d1))
* remove phantom sk/type fields from Game type ([016d306](https://github.com/Strandgaard96/mc-gamertime/commit/016d306f14fa0ad249acafeec1698d710fd9bcc5))
* replace uv pip -t with --target for lambda build ([a733e57](https://github.com/Strandgaard96/mc-gamertime/commit/a733e57a08c863d542071158d7bce9928fde0a74))
* resolve tailwind-merge transition conflict in pressable ([f4e2917](https://github.com/Strandgaard96/mc-gamertime/commit/f4e2917653bac15eb7688b2addcfbd4ac1f2e6eb))
* return 404 when deleting non-existent game or recommendation ([b6ff267](https://github.com/Strandgaard96/mc-gamertime/commit/b6ff2674437494f2292129eb6d02c404aa5a2b65))
* revoke sessions on password change, validate result edit fields ([7e181b2](https://github.com/Strandgaard96/mc-gamertime/commit/7e181b20ed9538019b895480386e58725c88c1dd))
* **scripts:** create-user.py respects USERS_TABLE/AWS_REGION env vars ([f875000](https://github.com/Strandgaard96/mc-gamertime/commit/f87500020e84f46b69a8276d6b810eade8dfd523))
* seed game in winner-not-in-players test to test correct validation ([5c1fccf](https://github.com/Strandgaard96/mc-gamertime/commit/5c1fccf7a7acf9ad07996cc360fd032d3a384f7d))
* **selfhost:** add necessary capabilities for bind mounts and update seaweedfs healthcheck ([0271747](https://github.com/Strandgaard96/mc-gamertime/commit/0271747c531eda6b84f196bea460df96e6ced4cd))
* show hover cue only on clickable rec cards ([12eb343](https://github.com/Strandgaard96/mc-gamertime/commit/12eb343aa7ac5598c754c81629b061458dfda555))
* show threshold placeholders when stats cards are absent ([c1291f6](https://github.com/Strandgaard96/mc-gamertime/commit/c1291f67fd98833f505c946f1e0d2b5459e58224))
* skip auth spinner on public routes — landing page paints immediately ([c428629](https://github.com/Strandgaard96/mc-gamertime/commit/c4286297fd18b187da62b655d5542394dc9f5df1))
* skip malformed player entries in compute_stats ([fd9fc5b](https://github.com/Strandgaard96/mc-gamertime/commit/fd9fc5b34a077eb067867e0f5ec1dcf92b2d0077))
* surface 429 Retry-After on login lockout ([91a96b6](https://github.com/Strandgaard96/mc-gamertime/commit/91a96b679eda85f550795b90cf427bebc2fbcc10))
* surface backend error messages in log-game and create-user toasts ([386e709](https://github.com/Strandgaard96/mc-gamertime/commit/386e70981c9335c03d31125d8fb9def71e83844f))
* transparent favicon background ([8885c70](https://github.com/Strandgaard96/mc-gamertime/commit/8885c702c11b7a8b09bc990dd21badd5c6e58295))
* typo in landing page heading; remove commented-out code ([e5b09ce](https://github.com/Strandgaard96/mc-gamertime/commit/e5b09ce7fdba772f636921c74a86dca96748716d))
* update create-user for new schema; add list-users script and task commands ([3690ed0](https://github.com/Strandgaard96/mc-gamertime/commit/3690ed0af38951440f6fc3236c50d1dfbcb8355e))
* use apiFetch for recommended endpoints to enable consistent 401 handling ([406f0f2](https://github.com/Strandgaard96/mc-gamertime/commit/406f0f2b9dbfac0efb13e9619b37f9fe669a6213))
* use clean white destructive-foreground, fix obsidian muted saturation ([deb6f1e](https://github.com/Strandgaard96/mc-gamertime/commit/deb6f1e8b3e69211e9543325bc1d6564f81c4d4d))
* use min-h-dvh to stabilise mobile bottom nav ([8bc1c07](https://github.com/Strandgaard96/mc-gamertime/commit/8bc1c079fb9a24d49059bfa48a786270be295aa9))
* use object-contain on recommended page game images ([007d975](https://github.com/Strandgaard96/mc-gamertime/commit/007d9753c48d1076349a942532d0a6e7e32aee03))
* UX/UI improvements across catalog, results, and leaderboard ([e3566a6](https://github.com/Strandgaard96/mc-gamertime/commit/e3566a6872001054981927c9c9da649dfe325e6a))
* validate non-empty title and content in CreatePostBody ([bb76784](https://github.com/Strandgaard96/mc-gamertime/commit/bb76784306a7cca8d952b07f0b80930e13a4ec74))
* validate saved theme against THEMES before applying to DOM ([b72ab23](https://github.com/Strandgaard96/mc-gamertime/commit/b72ab23f769b67056a40c47a46c7d37ee31c9787))
* **web:** add inline player creation to LogResult dialog and player profile links to leaderboard and results ([809bcd4](https://github.com/Strandgaard96/mc-gamertime/commit/809bcd4d547fa4aabdcf9b5d584ebe43924881d2))
* **web:** avoid login-form flash for already-authenticated visitors ([5b2c4ea](https://github.com/Strandgaard96/mc-gamertime/commit/5b2c4eadb4be9681b48d3eb600e5d83abed8ff11))
* **web:** correct outro slide copy on Wrapped overlay ([eff50cf](https://github.com/Strandgaard96/mc-gamertime/commit/eff50cfeeb60591d89cbdac9e074de1e5b2369ad))
* **web:** fix blog post body text invisible on dark themes ([1f7a059](https://github.com/Strandgaard96/mc-gamertime/commit/1f7a059f4538780f07203a876f5dc9de57a03390))
* **web:** getCurrentUser uses raw fetch to avoid 401 redirect on public pages ([6a69fb2](https://github.com/Strandgaard96/mc-gamertime/commit/6a69fb28cfd94348ba1cb5eb420f7e665087cd7b))
* **web:** link user rows to player profile page ([477d179](https://github.com/Strandgaard96/mc-gamertime/commit/477d17901382be3e30a92662c01b4e2b9624f028))
* **web:** move desktop nav breakpoint to lg to prevent tablet overflow ([ce6b84b](https://github.com/Strandgaard96/mc-gamertime/commit/ce6b84b600212b0545b333e8e13a18cbcca1f294))
* **web:** pluralize session count on home page ([4e6fcb0](https://github.com/Strandgaard96/mc-gamertime/commit/4e6fcb0f368216746c0c354ad7236590ca13b8b8))
* **web:** preserve comment text on submit failure, label reaction picker ([67e72d4](https://github.com/Strandgaard96/mc-gamertime/commit/67e72d4f410e846164302b8e62b0afcf08082bc2))
* **web:** prevent stale variable keys and game-switch state leakage in LogResultDialog ([7f7cb46](https://github.com/Strandgaard96/mc-gamertime/commit/7f7cb46c9b162b7cfe90ec1dad6bb3c484e1a1de))
* **web:** remove duplicate count in HomePage session-logged text ([da77aee](https://github.com/Strandgaard96/mc-gamertime/commit/da77aee5762ff39d61b14e9ebb9f2201241f9f5e))
* **web:** remove nested &lt;a&gt;&lt;button&gt; on LandingPage sign-in links ([117faf0](https://github.com/Strandgaard96/mc-gamertime/commit/117faf06705ea45996cd9d5050d850b7e6642785))
* **web:** remove nested &lt;a&gt;&lt;button&gt; on PostEditorPage cancel link ([2a7eee0](https://github.com/Strandgaard96/mc-gamertime/commit/2a7eee069f261156cd056d5337b946b09750e7b4))
* **web:** remove nested &lt;a&gt;&lt;button&gt; on PostsPage new-post links ([708cd70](https://github.com/Strandgaard96/mc-gamertime/commit/708cd7061d533706c0771f618a8384894d6243c9))
* **web:** remove nested &lt;a&gt;&lt;button&gt; on RecDetailPage sign-in links ([92c3a4b](https://github.com/Strandgaard96/mc-gamertime/commit/92c3a4b1ffccd1b025248f527ec4aa35a0307d0f))
* **web:** remove nested &lt;a&gt;&lt;button&gt; on RecommendedPage sign-in link ([8713201](https://github.com/Strandgaard96/mc-gamertime/commit/87132013bc19e976e642a65d858fc5085c6fa876))
* **web:** scope WrappedOverlay keydown effect and improve a11y ([803e82b](https://github.com/Strandgaard96/mc-gamertime/commit/803e82bf2309575a987616b65c6a30fd4f70db85))
* **web:** show Elo rating on records page champion card ([feef3de](https://github.com/Strandgaard96/mc-gamertime/commit/feef3dea404b69c539138b15cde015c5f1c647ab))
* **web:** use registered users as players in LogResult, link nav username to profile ([bb0d9e8](https://github.com/Strandgaard96/mc-gamertime/commit/bb0d9e88e0834d827e791cc764108097ab211123))
* WinRaceChart hidden-player tooltip, duplicate ticks, connectNulls bridge ([5bec521](https://github.com/Strandgaard96/mc-gamertime/commit/5bec52123a05f9f729fe5eb9b329a1536d6bb68f))


### Reverts

* remove CloudFront response headers policy (not supported on free pricing plan) ([d0748d6](https://github.com/Strandgaard96/mc-gamertime/commit/d0748d68d34b711718a17fc9096ccc5e0a1ffeca))

## Changelog
