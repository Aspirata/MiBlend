# AGENTS.md

## Scope

These instructions apply to the entire repository. MiBlend is a beta Blender extension for building Minecraft scenes. Keep changes focused, preserve existing user work, and do not rewrite unrelated code or binary assets.

## Project map

- `MiBlend_Source/` is the distributable add-on/extension source.
  - `__init__.py` owns add-on registration, the persistent scene-load handler, and delayed startup initialization.
  - `blender_manifest.toml` is the Blender extension manifest. The current minimum supported Blender version is 4.2.
  - `panels/` contains feature modules: `world`, `materials`, `procedural_pbr`, `environment`, `resource_packs`, `assets`, `absolute_solver`, and `debug`.
  - `mib_utils.py` contains shared Blender/node/material/path/debug helpers.
  - `resources/data.py` defines packaged paths and Minecraft material classification data. Files in `resources/`, especially `.blend` libraries, are runtime dependencies.
  - `Assets/` contains user-importable rigs, node groups, and scripts. Most assets are a metadata JSON file plus a same-basename `.blend` or `.py` payload.
  - `Resource Packs/` contains bundled third-party resource-pack data and `packs_info.json`.
- `scripts/` contains local build helpers.
- `bpy-build.yaml` configures `bpy-addon-build`; its default build excludes `Resource Packs`.
- `.github/workflows/Addon Build.yaml` only packages the source on pushes and pull requests to `Experimental`; it is not a test suite.
- `Debug/` and the root `MiBlend.blend` are large Blender development/fixture files. Do not change them unless the task explicitly requires Blender scene data.
- `docs/` and `docs.json` drive the published documentation.
- `build/` and root ZIP files are generated outputs and are ignored by Git.

## Runtime and architecture

- Production code runs inside Blender and imports `bpy`; a normal system Python cannot import the add-on end-to-end.
- Preserve compatibility with Blender 4.2+ and existing explicit version branches for Blender 4.x/5.x APIs. Do not replace guarded API access with a single-version implementation.
- Feature modules normally separate responsibilities as follows:
  - `*_properties.py`: Blender `PropertyGroup` definitions.
  - `*_ui.py`: panels and layout only.
  - `*_operators.py`: Blender operators that validate/forward context and return Blender status sets.
  - `*_logic.py`: scene, material, node, asset, or filesystem behavior.
  - `__init__.py`: the module's ordered `classes` registration list.
- Registration flows from each feature's `classes` list to `MiBlend_Source/panels/__init__.py`, then to `MiBlend_Source/__init__.py`. When adding a panel, operator, UI list, or property group, update every relevant registration/aggregation list.
- Scene properties live under `context.scene.miblend_properties`. The root pointer is installed during `register()` and removed during `unregister()`.
- Startup also maintains scene ID properties named `resource_packs` and `mib_options`. Existing key spellings such as `components_vesion`, datablock names, socket names, custom-property names, and `MiBlend ID`/`MiBlend_ID` may be persisted in `.blend` files; do not "correct" or rename them without a migration.
- `init_on_start()` runs through Blender timers both on registration and after scene load. Startup work must tolerate missing/legacy scene state and should report unexpected failures through Absolute Solver.
- `absolute_solver` is the user-facing error/warning path. Codes use `wNN`, `eNN`, and `nNN`, with text in `absolute_solver_list.json`. Add or change the English and `_ru` fields together, keep placeholders compatible with `.format(Data=...)`, and ensure any operator IDs in `Solutions` are registered.
- Shared node groups and materials are loaded from packaged `.blend` libraries by exact datablock and socket names. Treat those names as interfaces shared by Python and binary resources.
- Resource-pack code can download from Modrinth, extract archives, write `packs_info.json`, and replace files. Keep network/filesystem behavior behind explicit user actions or the existing `update_packs` preference; never introduce import-time network access.
- Asset scripts are executed dynamically with `properties` plus public names from `resources.data` and `mib_utils`. Changing that execution context is a compatibility change.

## Code conventions

- Match the local style in the file being edited; this repository does not have an enforced formatter or linter. Avoid broad formatting-only changes.
- Use four-space indentation and keep source/metadata text UTF-8.
- Follow Blender naming conventions already used by the project:
  - `MIBLEND_PG_*` for property groups.
  - `MIBLEND_PT_*` for panels.
  - `MIBLEND_OT_*` for operators.
  - `MIBLEND_UL_*` for UI lists.
  - `bl_idname` values use the `miblend.` prefix.
- Prefer explicit relative imports within the add-on. Use `get_preferences()` instead of duplicating add-on lookup logic.
- Keep UI draw methods lightweight. Put reusable or nontrivial Blender mutations in the feature's logic module and keep operators thin.
- Use `dprint()` for optional diagnostics, its existing zone names for feature-specific logging, and `@perf_time` for established major operations. Do not add unconditional noisy prints to production paths.
- Report recoverable user-facing failures with `trigger_absolute_solver()` where the surrounding module already follows that pattern. Preserve tracebacks for unexpected internal failures.
- Blender operations depend heavily on active object, selection, mode, current area, and current scene. When code changes any of these, restore prior state when practical and test empty selections, non-mesh objects, missing materials/images/node trees, and absent datablocks.
- Prefer the path constants in `resources/data.py` over working-directory-dependent paths. Code must work from an installed extension, not only from the repository root.
- Avoid wildcard imports in new code even though legacy code contains one. Do not perform large refactors of `mib_utils.py` or `resource_packs_logic.py` as collateral work.

## Assets, JSON, and binary files

- Asset discovery recursively scans JSON metadata. For normal assets, `Format_version`, `Asset_name`, `Author`, and a non-empty `Tags` list are required; the first tag determines the asset type.
- The payload must share the JSON basename: scripts use `.py`; other assets use `.blend`. If a helper script accompanies a node asset, it also shares the basename.
- Metadata keys ending in `_property` become configurable values exposed to the asset script. Preserve key spelling and value type.
- Keep metadata names synchronized with exact collection, material, node-group, and Blender-version constraints inside the corresponding `.blend` file.
- Validate JSON after edits. Preserve both English and Russian Absolute Solver text when changing diagnostics.
- Do not resave `.blend`, image, archive, or resource-pack files just to normalize them. Binary changes are difficult to review and often create very large diffs.
- Preserve third-party attribution and licensing information when changing bundled rigs or resource packs.

## Validation

Run the smallest relevant checks first. There is currently no automated unit-test suite.

1. Syntax-check all Python without importing `bpy` or creating `__pycache__`:

   ```powershell
   python -c "from pathlib import Path; f=list(Path('MiBlend_Source').rglob('*.py'))+list(Path('scripts').glob('*.py')); [compile(p.read_bytes(), str(p), 'exec') for p in f]; print(f'{len(f)} Python files OK')"
   ```

2. When JSON changes, parse all packaged JSON:

   ```powershell
   python -c "import json; from pathlib import Path; f=list(Path('MiBlend_Source').rglob('*.json')); [json.loads(p.read_text(encoding='utf-8')) for p in f]; print(f'{len(f)} JSON files OK')"
   ```

3. When the manifest changes and Python 3.11+ is available:

   ```powershell
   python -c "import tomllib; tomllib.loads(open('MiBlend_Source/blender_manifest.toml', encoding='utf-8').read()); print('Manifest OK')"
   ```

4. For registration, UI, node, scene, or compatibility changes, test in Blender 4.2+ using a disposable `.blend` file. At minimum: enable/disable the extension without registration errors, open the affected panel, run the affected operator on valid and empty/invalid selections, save/reload the scene, and inspect the system console/Absolute Solver.

5. For cross-version API changes, test the affected path on both the oldest supported Blender line and the newest targeted line when possible.

6. For a package smoke test, run `bab` from the repository root if `bpy-addon-build` is already installed. The wrappers `bab_build_win.cmd` and `bab_build_unix.sh` install build dependencies and then run `scripts/build_universal.py`; that script may terminate a Blender process whose command line references MiBlend, so do not run it during an active Blender session without warning the user.

7. `release_build_win.cmd` / `release_build_unix.sh` invoke an interactive release archiver that creates `MiBlend.zip`. Use it only for an explicit release task, not routine validation.

## Change checklist

- Inspect `git status` before and after editing; preserve unrelated modified files.
- Keep source changes under `MiBlend_Source/` unless the task is specifically about tooling, docs, or fixtures.
- If adding a Blender class, verify its registration order and successful unregister/re-register behavior.
- If adding persisted properties or changing hard-version/component state, consider migration behavior for existing `.blend` files.
- If changing a node/socket/datablock name, update Python and the owning `.blend` library together and call out the binary change.
- If changing an asset, validate metadata plus the same-basename payload.
- If changing resource-pack code, exercise directory and ZIP/JAR paths and prevent traversal or unintended deletion outside the selected pack directory.
- Report which checks were run and which Blender/manual checks were not available.
