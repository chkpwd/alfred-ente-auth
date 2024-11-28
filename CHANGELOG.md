# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.2.1] - 2024-11-28
### :bug: Bug Fixes
- [`8722385`](https://github.com/chkpwd/alfred-ente-auth/commit/872238505f61dcb399bb89595accd3dbcf32b0da) - **ente_auth**: use defined binary path *(commit by [@tigattack](https://github.com/tigattack))*
- [`0b774ed`](https://github.com/chkpwd/alfred-ente-auth/commit/0b774ed8436d777f54025335f75ab26d5dce705f) - **ente_auth**: correctly assign binary path when defined by user *(commit by [@tigattack](https://github.com/tigattack))*
- [`cb0cc15`](https://github.com/chkpwd/alfred-ente-auth/commit/cb0cc159dce8ce8b5faebeb101c41e17cbe67c99) - set uid for each item in Alfred response *(commit by [@tigattack](https://github.com/tigattack))*

### :wrench: Chores
- [`2e9ef2e`](https://github.com/chkpwd/alfred-ente-auth/commit/2e9ef2ea526415f9b98ca18ab1f68c7e4f4b4fdd) - bump version *(commit by [@tigattack](https://github.com/tigattack))*


## [v2.2.0] - 2024-11-28
### :sparkles: New Features
- [`4c2be35`](https://github.com/chkpwd/alfred-ente-auth/commit/4c2be35137cd6cc6054c0750d2473b16eeef34ce) - return all accounts, filter in Alfred *(commit by [@tigattack](https://github.com/tigattack))*
- [`e05c79b`](https://github.com/chkpwd/alfred-ente-auth/commit/e05c79b8c6687ec3803da79cce3f665e3dc8819a) - refresh results every second *(commit by [@tigattack](https://github.com/tigattack))*
- [`c3d5f50`](https://github.com/chkpwd/alfred-ente-auth/commit/c3d5f5094781089e897349536775b9be0b11f64d) - support any TOTP refresh period *(commit by [@tigattack](https://github.com/tigattack))*
- [`bf09891`](https://github.com/chkpwd/alfred-ente-auth/commit/bf0989133d66e8f0868bf24f31ff7e0a1bdd6d13) - run import script via keyword to avoid account search *(commit by [@tigattack](https://github.com/tigattack))*

### :bug: Bug Fixes
- [`1862039`](https://github.com/chkpwd/alfred-ente-auth/commit/1862039abe7b8e7ca16e9482deae3c5449689238) - remove duplicated constants *(commit by [@tigattack](https://github.com/tigattack))*
- [`e014ab4`](https://github.com/chkpwd/alfred-ente-auth/commit/e014ab49eaa0cbde90a6cade16ae80c0180f675c) - correctly utilise Alfred script filter variables *(commit by [@tigattack](https://github.com/tigattack))*
- [`9c77a1b`](https://github.com/chkpwd/alfred-ente-auth/commit/9c77a1b62a91902dd018fc890cbf4f20bfc9a00c) - consistently sanitise service names *(commit by [@tigattack](https://github.com/tigattack))*
- [`e14e5aa`](https://github.com/chkpwd/alfred-ente-auth/commit/e14e5aa2f0e59000a86d86b79022f1619992c76d) - set `match` attr in accounts output to Alfred *(commit by [@tigattack](https://github.com/tigattack))*
- [`043a0f1`](https://github.com/chkpwd/alfred-ente-auth/commit/043a0f1482ba617dcc291517ff223e46d4cced01) - don't include empty values output *(commit by [@tigattack](https://github.com/tigattack))*
- [`a760584`](https://github.com/chkpwd/alfred-ente-auth/commit/a76058447ab65240367eade614a8bf2d5c57ca9d) - don't include Alfred session cache in import response *(commit by [@tigattack](https://github.com/tigattack))*

### :recycle: Refactors
- [`bc5039a`](https://github.com/chkpwd/alfred-ente-auth/commit/bc5039a4b203b05348655a4a87f3fc147b0ecd07) - remove redundant condition *(commit by [@tigattack](https://github.com/tigattack))*
- [`a18ec85`](https://github.com/chkpwd/alfred-ente-auth/commit/a18ec85781ed5549e8651e9123a425b839789ae3) - simplify `ente_export_to_keychain` error handling *(commit by [@tigattack](https://github.com/tigattack))*
- [`f09745a`](https://github.com/chkpwd/alfred-ente-auth/commit/f09745a2326b42418e1f39d23519ff3278209d79) - add `PYTHONPATH` to workflow env to replace `PATH` mangling *(commit by [@tigattack](https://github.com/tigattack))*
- [`25965f0`](https://github.com/chkpwd/alfred-ente-auth/commit/25965f0dc5fcf74ea89b1b6db37ac03fe8525e3a) - remove redundant f-string *(commit by [@tigattack](https://github.com/tigattack))*
- [`ca461fb`](https://github.com/chkpwd/alfred-ente-auth/commit/ca461fb92ae38e55f225aee8f744d1ecb7d0e0b2) - improve type hints and docstrings *(commit by [@tigattack](https://github.com/tigattack))*
- [`d173c71`](https://github.com/chkpwd/alfred-ente-auth/commit/d173c71fe7c59a317a2fca31dbb531530e976867) - **icon_downloader**: rename funcs, improve logging, relocate consts *(commit by [@tigattack](https://github.com/tigattack))*
- [`11dbac6`](https://github.com/chkpwd/alfred-ente-auth/commit/11dbac63a87e3aa68aa13523a7d3d79369de95f2) - improve build script *(commit by [@tigattack](https://github.com/tigattack))*

### :wrench: Chores
- [`92a2b3d`](https://github.com/chkpwd/alfred-ente-auth/commit/92a2b3dc6e10eb560e76df488a5f354edbfe7ecd) - remove default value and clarify info for `ENTE_EXPORT_DIR` *(commit by [@tigattack](https://github.com/tigattack))*
- [`3148833`](https://github.com/chkpwd/alfred-ente-auth/commit/3148833a4f174f92303649a8bf63a22fedf6a056) - define workflow category *(commit by [@tigattack](https://github.com/tigattack))*
- [`a0c1165`](https://github.com/chkpwd/alfred-ente-auth/commit/a0c11658f3edea9fe79df18a3192b46644187b78) - add info for `OVERWRITE_EXPORT` setting *(commit by [@tigattack](https://github.com/tigattack))*
- [`61514dd`](https://github.com/chkpwd/alfred-ente-auth/commit/61514dd4b77fa579e8d1e9d3de98f26342502c24) - bump workflow version *(commit by [@tigattack](https://github.com/tigattack))*


## [v2.1.0] - 2024-11-26
### :sparkles: New Features
- [`dd2cb41`](https://github.com/chkpwd/alfred-ente-auth/commit/dd2cb410d529cdc17008dc8cf756a432890b5eb6) - grab service names from cache *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`817f150`](https://github.com/chkpwd/alfred-ente-auth/commit/817f15023b2b0a42d06a9f5f1455867473871513) - add name sanitazion *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`49fac49`](https://github.com/chkpwd/alfred-ente-auth/commit/49fac494f409751ed5a47354dec69c06dc63e2d1) - add simplepycons dep *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`ae3d4ba`](https://github.com/chkpwd/alfred-ente-auth/commit/ae3d4ba2b1cb8e5d18f57adfe61fd7507d3c86e7) - grab icons from multiple sources *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`997d0db`](https://github.com/chkpwd/alfred-ente-auth/commit/997d0db6e59036afb8556adf397c045423641478) - set primary_color to svg fill attr *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`62874fe`](https://github.com/chkpwd/alfred-ente-auth/commit/62874fefac00cf40a11c43d2a3ebfb1b6e747356) - bump version *(commit by [@chkpwd](https://github.com/chkpwd))*

### :bug: Bug Fixes
- [`1b2e858`](https://github.com/chkpwd/alfred-ente-auth/commit/1b2e85819874cce12b97e8b89c11bd0f06accd3e) - typo found *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`c775c9d`](https://github.com/chkpwd/alfred-ente-auth/commit/c775c9dfcb402dbfc372c16ac3b00b5cb6f6ca23) - variable call *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`a7be5dd`](https://github.com/chkpwd/alfred-ente-auth/commit/a7be5dda719afebd9dc61a5113439cfa202c24b6) - ensure output does not return None *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`adc052f`](https://github.com/chkpwd/alfred-ente-auth/commit/adc052f584945f598378e6df003a57cbe87667f3) - **workflow**: install poetry before setting up python *(commit by [@chkpwd](https://github.com/chkpwd))*

### :wrench: Chores
- [`7041daa`](https://github.com/chkpwd/alfred-ente-auth/commit/7041daa57812970920364eeee0b0b43cfdcfdc26) - made readme better *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`177d3fd`](https://github.com/chkpwd/alfred-ente-auth/commit/177d3fd521fe3487cd7e7b25b96309d82b093fac) - improve logging *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`9942848`](https://github.com/chkpwd/alfred-ente-auth/commit/9942848f149694694e6dc7c829848fd07d57be0e) - place constants globally *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`b07d71c`](https://github.com/chkpwd/alfred-ente-auth/commit/b07d71cdd5793caa0310e0db3e2f1fb1ff15a0b5) - add additional imports *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`861693f`](https://github.com/chkpwd/alfred-ente-auth/commit/861693f5764c550cf6fbe2936e11ff1beefddffb) - adjust logging message to reflect actions *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`f7e2369`](https://github.com/chkpwd/alfred-ente-auth/commit/f7e23691cfd8e5059ddb33ee67a3fa237dbef7b8) - adjust imports for constants *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`a5769af`](https://github.com/chkpwd/alfred-ente-auth/commit/a5769afc44a7e3b2094051aaa7a7a628220f9c55) - set icon path to the class *(commit by [@chkpwd](https://github.com/chkpwd))*


## [v2.0.0] - 2024-11-15
### :bug: Bug Fixes
- [`e98176d`](https://github.com/chkpwd/alfred-ente-auth/commit/e98176d84cbe49e9353571e1fefa570c5317c0ba) - find python dir then append to sys.path *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`1a06e1e`](https://github.com/chkpwd/alfred-ente-auth/commit/1a06e1e39755676e312539b2d7d48323e5e7da99) - setup python *(commit by [@chkpwd](https://github.com/chkpwd))*
- [`7488e96`](https://github.com/chkpwd/alfred-ente-auth/commit/7488e96dd6a3405d45147c42d3f25b2ac94be48b) - add poetry dep *(commit by [@chkpwd](https://github.com/chkpwd))*

[v2.0.0]: https://github.com/chkpwd/alfred-ente-auth/compare/latest...v2.0.0
[v2.1.0]: https://github.com/chkpwd/alfred-ente-auth/compare/v2.0.0...v2.1.0
[v2.2.0]: https://github.com/chkpwd/alfred-ente-auth/compare/v2.1.0...v2.2.0
[v2.2.1]: https://github.com/chkpwd/alfred-ente-auth/compare/v2.2.0...v2.2.1
