"""Run MiBlend's Blender integration scenario and produce a CI report.

The script has two roles. System Python orchestrates isolated Blender
processes, while Blender executes either the core pipeline or one asset.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import traceback
from collections import deque
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ERROR_PREFIXES = ("e", "n")
RESOURCE_PACKS = ("Bare Bones", "Embrace Pixels")


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MiBlend in Blender")
    parser.add_argument("--blender", type=Path)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--worker", choices=("core", "asset"))
    parser.add_argument("--result", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--asset-name")
    parser.add_argument("--asset-path")
    return parser.parse_args(argv)


def blender_arguments() -> list[str]:
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1:]


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return cleaned or "unnamed_asset"


def github_escape(message: object) -> str:
    return (
        str(message)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )


def annotation(kind: str, title: str, message: object) -> None:
    print(
        f"::{kind} title={github_escape(title)}::{github_escape(message)}",
        flush=True,
    )


def result_line(status: str, label: str, duration: float | None = None) -> None:
    suffix = "" if duration is None else f" {duration:.2f}s"
    print(f"[{status}] {label}{suffix}", flush=True)


def run_blender_worker(
        blender: Path,
        worker_args: list[str],
        log_file,
        title: str,
) -> tuple[int, bool]:
    command = [
        str(blender),
        "--background",
        "--factory-startup",
        "--python",
        str(SCRIPT_PATH),
        "--",
        *worker_args,
    ]
    print(f"::group::{github_escape(title)}", flush=True)
    saw_traceback = False
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=os.environ.copy(),
    )
    assert process.stdout is not None
    tail: deque[str] = deque(maxlen=80)
    for line in process.stdout:
        log_file.write(line)
        log_file.flush()
        tail.append(line)
        if "Traceback (most recent call last):" in line:
            saw_traceback = True
    return_code = process.wait()
    if return_code != 0 or saw_traceback:
        print("".join(tail), end="", flush=True)
    print("::endgroup::", flush=True)
    return return_code, saw_traceback


def worker_common_args(args: argparse.Namespace) -> list[str]:
    return [
        "--source-root", str(args.source_root.resolve()),
        "--fixture", str(args.fixture.resolve()),
        "--output-dir", str(args.output_dir.resolve()),
    ]


def combine_report(
        core: dict[str, Any],
        asset_results: list[dict[str, Any]],
        orchestration_errors: list[str],
) -> dict[str, Any]:
    skipped = core.get("assets", {}).get("skipped", [])
    failed_assets = [item for item in asset_results if item.get("status") != "passed"]
    warnings = list(core.get("warnings", []))
    for item in asset_results:
        warnings.extend(item.get("warnings", []))

    status = "passed"
    if core.get("status") != "passed" or failed_assets or orchestration_errors:
        status = "failed"

    return {
        "status": status,
        "blender": core.get("blender", {}),
        "fixture": core.get("fixture", {}),
        "core_steps": core.get("steps", []),
        "assets": {
            "passed": [
                item.get("asset_name", "Unknown")
                for item in asset_results
                if item.get("status") == "passed"
            ],
            "failed": failed_assets,
            "skipped": skipped,
        },
        "warnings": warnings,
        "errors": list(core.get("errors", [])) + orchestration_errors,
        "duration_seconds": core.get("duration_seconds", 0.0)
        + sum(float(item.get("duration_seconds", 0.0)) for item in asset_results),
    }


def markdown_summary(report: dict[str, Any]) -> str:
    blender = report.get("blender", {})
    version = blender.get("version_string", "unknown")
    status = report.get("status", "failed").upper()
    lines = [
        f"## MiBlend CI — Blender {version}",
        "",
        f"**Result: {status}**",
        "",
        "| Stage | Result | Time |",
        "|---|---:|---:|",
    ]
    for step in report.get("core_steps", []):
        lines.append(
            f"| {step.get('name', 'Unknown')} | "
            f"{step.get('status', 'failed').upper()} | "
            f"{float(step.get('duration_seconds', 0.0)):.2f}s |"
        )

    assets = report.get("assets", {})
    passed = len(assets.get("passed", []))
    failed = len(assets.get("failed", []))
    skipped = len(assets.get("skipped", []))
    lines.extend([
        "",
        f"- Assets passed: {passed}",
        f"- Assets failed: {failed}",
        f"- Assets skipped: {skipped}",
        f"- Warnings: {len(report.get('warnings', []))}",
        f"- Total time: {float(report.get('duration_seconds', 0.0)):.2f}s",
    ])

    if assets.get("failed"):
        lines.extend(["", "### Failed assets", ""])
        for item in assets["failed"]:
            lines.append(
                f"- **{item.get('asset_name', 'Unknown')}**: "
                f"{item.get('message', 'Unknown failure')}"
            )

    if assets.get("skipped"):
        lines.extend(["", "### Skipped assets", ""])
        for item in assets["skipped"]:
            requirement = item.get("requirement", ">= 4.2.0")
            lines.append(f"- {item.get('name', 'Unknown')} — requires {requirement}")

    if report.get("errors"):
        lines.extend(["", "### Errors", ""])
        for error in report["errors"]:
            lines.append(f"- {error}")

    return "\n".join(lines) + "\n"


def orchestrate(args: argparse.Namespace) -> int:
    started = time.perf_counter()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "blender.log"
    report_path = output_dir / "report.json"
    summary_path = output_dir / "summary.md"
    checkpoint = output_dir / "miblend_ci_test.blend"
    core_result_path = output_dir / "core-result.json"
    orchestration_errors: list[str] = []
    asset_results: list[dict[str, Any]] = []

    if args.blender is None or not args.blender.is_file():
        orchestration_errors.append(f"Blender executable not found: {args.blender}")
    if not args.fixture.is_file():
        orchestration_errors.append(f"Fixture not found: {args.fixture}")
    if not (args.source_root / "__init__.py").is_file():
        orchestration_errors.append(f"MiBlend source not found: {args.source_root}")

    core: dict[str, Any] = {
        "status": "failed",
        "errors": [],
        "steps": [],
        "assets": {"compatible": [], "skipped": []},
    }

    with log_path.open("w", encoding="utf-8", errors="replace") as log_file:
        if not orchestration_errors:
            core_args = [
                "--worker", "core",
                *worker_common_args(args),
                "--result", str(core_result_path),
                "--checkpoint", str(checkpoint),
            ]
            return_code, saw_traceback = run_blender_worker(
                args.blender.resolve(),
                core_args,
                log_file,
                "Core pipeline",
            )
            core = read_json(core_result_path) or {
                "status": "failed",
                "errors": ["Core worker did not produce a valid result"],
                "steps": [],
                "assets": {"compatible": [], "skipped": []},
            }
            if return_code != 0:
                orchestration_errors.append(
                    f"Core Blender process exited with code {return_code}"
                )
            if saw_traceback and core.get("status") == "passed":
                orchestration_errors.append("Core Blender log contains a traceback")

        if core.get("status") == "passed" and not orchestration_errors:
            compatible_assets = core.get("assets", {}).get("compatible", [])
            for position, asset in enumerate(compatible_assets, start=1):
                asset_name = asset.get("name", "Unknown")
                asset_result_path = (
                    output_dir / "asset-results" / f"{position:03d}.json"
                )
                worker_args = [
                    "--worker", "asset",
                    *worker_common_args(args),
                    "--result", str(asset_result_path),
                    "--checkpoint", str(checkpoint),
                    "--asset-name", asset_name,
                    "--asset-path", asset.get("path", ""),
                ]
                return_code, saw_traceback = run_blender_worker(
                    args.blender.resolve(),
                    worker_args,
                    log_file,
                    f"Asset {position}/{len(compatible_assets)}: {asset_name}",
                )
                asset_result = read_json(asset_result_path) or {
                    "status": "failed",
                    "asset_name": asset_name,
                    "message": "Asset worker did not produce a valid result",
                    "warnings": [],
                    "duration_seconds": 0.0,
                }
                if return_code != 0:
                    asset_result["status"] = "failed"
                    asset_result["message"] = (
                        f"Blender process exited with code {return_code}"
                    )
                elif saw_traceback and asset_result.get("status") == "passed":
                    asset_result["status"] = "failed"
                    asset_result["message"] = "Blender log contains a traceback"
                if asset_result.get("status") == "passed":
                    result_scene = asset_result.get("result_scene")
                    if result_scene:
                        try:
                            Path(result_scene).unlink()
                        except OSError as error:
                            orchestration_errors.append(
                                f"Could not remove successful asset scene "
                                f"{result_scene}: {error}"
                            )
                asset_results.append(asset_result)

    report = combine_report(core, asset_results, orchestration_errors)
    report["wall_time_seconds"] = time.perf_counter() - started
    write_json(report_path, report)
    summary_path.write_text(markdown_summary(report), encoding="utf-8")

    for step in report.get("core_steps", []):
        result_line(
            "PASS" if step.get("status") == "passed" else "FAIL",
            step.get("name", "Unknown stage"),
            float(step.get("duration_seconds", 0.0)),
        )
    for item in report.get("assets", {}).get("passed", []):
        result_line("PASS", item)
    for item in report.get("assets", {}).get("skipped", []):
        result_line(
            "SKIP",
            f"{item.get('name', 'Unknown')} - requires "
            f"{item.get('requirement', '>= 4.2.0')}",
        )
    for item in report.get("assets", {}).get("failed", []):
        result_line("FAIL", item.get("asset_name", "Unknown"))
        annotation(
            "error",
            f"Asset failed: {item.get('asset_name', 'Unknown')}",
            item.get("message", "Unknown failure"),
        )
    for warning in report.get("warnings", []):
        annotation(
            "warning",
            f"MiBlend warning {warning.get('code', '')}",
            f"{warning.get('stage', 'unknown')}: {warning.get('data', '')}",
        )
    for error in report.get("errors", []):
        annotation("error", "MiBlend CI", error)

    result_line(
        "PASS" if report["status"] == "passed" else "FAIL",
        f"MiBlend CI ({report['wall_time_seconds']:.2f}s wall time)",
    )
    return 0 if report["status"] == "passed" else 1


class SolverCapture:
    def __init__(self) -> None:
        self.stage = "startup"
        self.records: list[dict[str, str]] = []

    def set_stage(self, stage: str) -> int:
        self.stage = stage
        return len(self.records)

    def __call__(
            self,
            code: str,
            tech_things: object = "",
            data: object = "",
    ) -> None:
        self.records.append({
            "stage": self.stage,
            "code": str(code),
            "data": str(data),
            "tech_things": str(tech_things),
        })

    def since(self, index: int) -> list[dict[str, str]]:
        return self.records[index:]


def solver_errors(records: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        record for record in records
        if record.get("code", "").startswith(ERROR_PREFIXES)
    ]


def patch_solver(miblend_module, capture: SolverCapture) -> None:
    prefix = miblend_module.__name__
    for module_name, module in list(sys.modules.items()):
        if not module_name.startswith(prefix) or module is None:
            continue
        if hasattr(module, "trigger_absolute_solver"):
            setattr(module, "trigger_absolute_solver", capture)


def enable_miblend(source_root: Path, capture: SolverCapture):
    import addon_utils
    import bpy

    package_parent = str(source_root.resolve().parent)
    if package_parent not in sys.path:
        sys.path.insert(0, package_parent)

    module_name = source_root.name
    module = addon_utils.enable(module_name, default_set=True, persistent=False)
    if module is None:
        raise RuntimeError(f"Failed to enable Blender add-on {module_name}")
    if module_name not in bpy.context.preferences.addons:
        raise RuntimeError(f"Preferences were not created for {module_name}")

    patch_solver(module, capture)
    preferences = bpy.context.preferences.addons[module_name].preferences
    preferences.update_packs = False
    preferences.dprint = False
    preferences.perf_time = False
    return module


def open_scene(path: Path, miblend_module) -> None:
    import bpy

    result = bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
    if "FINISHED" not in result:
        raise RuntimeError(f"Could not open Blender file: {path}")
    miblend_module.init_on_start()
    bpy.context.view_layer.update()


def selection_state() -> dict[str, Any]:
    import bpy

    active = bpy.context.view_layer.objects.active
    selected = list(bpy.context.selected_objects)
    if active is None or active.type != "MESH":
        raise RuntimeError("Fixture needs an active selected mesh object")
    if active not in selected:
        raise RuntimeError("The active mesh object must be selected")
    if not selected:
        raise RuntimeError("Fixture does not contain selected world objects")
    return {
        "active": active.name,
        "selected": [item.name for item in selected],
    }


def restore_selection(state: dict[str, Any]) -> None:
    import bpy

    bpy.ops.object.select_all(action="DESELECT")
    missing = []
    for name in state.get("selected", []):
        obj = bpy.data.objects.get(name)
        if obj is None:
            missing.append(name)
        else:
            obj.select_set(True)
    active = bpy.data.objects.get(state.get("active", ""))
    if active is None:
        missing.append(state.get("active", "<active object>"))
    if missing:
        raise RuntimeError(
            "Selected fixture objects disappeared: " + ", ".join(sorted(set(missing)))
        )
    bpy.context.view_layer.objects.active = active
    bpy.context.view_layer.update()


def run_operator_step(
        name: str,
        operator,
        capture: SolverCapture,
) -> dict[str, Any]:
    started = time.perf_counter()
    marker = capture.set_stage(name)
    try:
        result = operator()
        records = capture.since(marker)
        errors = solver_errors(records)
        if "FINISHED" not in result:
            raise RuntimeError(f"Operator returned {sorted(result)}")
        if errors:
            details = []
            for item in errors:
                technical = item.get("tech_things") or item.get("data") or ""
                details.append(f"{item['code']}: {technical}")
            raise RuntimeError(
                "Absolute Solver reported:\n" + "\n".join(details)
            )
        status = "passed"
        message = ""
    except Exception:
        status = "failed"
        message = traceback.format_exc()
        records = capture.since(marker)
    return {
        "name": name,
        "status": status,
        "message": message,
        "duration_seconds": time.perf_counter() - started,
        "solver": records,
    }


def save_scene(path: Path) -> None:
    import bpy

    path.parent.mkdir(parents=True, exist_ok=True)
    result = bpy.ops.wm.save_as_mainfile(filepath=str(path.resolve()), compress=True)
    if "FINISHED" not in result:
        raise RuntimeError(f"Could not save Blender file: {path}")


def enable_resource_packs() -> None:
    import bpy
    from MiBlend_Source.panels.resource_packs.resource_packs_logic import (
        get_resource_packs,
    )

    packs = get_resource_packs()
    for pack_name in RESOURCE_PACKS:
        if pack_name not in packs:
            raise RuntimeError(f"Bundled resource pack not found: {pack_name}")
        if not packs[pack_name].get("enabled", False):
            result = bpy.ops.miblend.toggle_resource_pack(pack_name=pack_name)
            if "FINISHED" not in result:
                raise RuntimeError(f"Could not enable resource pack: {pack_name}")
            packs = get_resource_packs()
        if not packs[pack_name].get("enabled", False):
            raise RuntimeError(f"Resource pack stayed disabled: {pack_name}")


def collect_assets() -> dict[str, list[dict[str, str]]]:
    import bpy
    from MiBlend_Source.panels.assets.assets_ui import MIBLEND_UL_assets

    result = bpy.ops.miblend.update_assets()
    if "FINISHED" not in result:
        raise RuntimeError(f"Update Assets returned {sorted(result)}")

    compatible: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    items = bpy.context.scene.miblend_properties.assets_properties.asset_items
    for item in items:
        name = item.get("Asset_name", "Unknown")
        requirement = item.get("Blender_version", ">= 4.2.0")
        entry = {
            "name": str(name),
            "path": str(item.get("File_path", "")),
            "requirement": str(requirement),
        }
        if MIBLEND_UL_assets.blender_version(requirement):
            compatible.append(entry)
        else:
            skipped.append(entry)
    return {"compatible": compatible, "skipped": skipped}


def warning_records(capture: SolverCapture) -> list[dict[str, str]]:
    return [
        record for record in capture.records
        if record.get("code", "").startswith("w")
    ]


def core_worker(args: argparse.Namespace) -> dict[str, Any]:
    import bpy

    started = time.perf_counter()
    capture = SolverCapture()
    result: dict[str, Any] = {
        "status": "failed",
        "steps": [],
        "errors": [],
        "warnings": [],
        "assets": {"compatible": [], "skipped": []},
        "fixture": {},
    }
    try:
        miblend = enable_miblend(args.source_root, capture)
        open_scene(args.fixture, miblend)
        state = selection_state()
        result["fixture"] = state
        startup_errors = solver_errors(capture.records)
        if startup_errors:
            codes = ", ".join(item["code"] for item in startup_errors)
            raise RuntimeError(f"MiBlend startup reported {codes}")

        steps = [
            (
                "Fix Materials",
                lambda: bpy.ops.miblend.materials_fix_materials(),
            ),
            (
                "Fix World",
                lambda: bpy.ops.miblend.fix_world(),
            ),
            (
                "Procedural PBR",
                lambda: bpy.ops.miblend.apply_procedural_pbr(),
            ),
            (
                "Resource Packs",
                lambda: (
                    enable_resource_packs(),
                    bpy.ops.miblend.apply_resource_pack(),
                )[1],
            ),
        ]
        for name, operator in steps:
            step = run_operator_step(name, operator, capture)
            result["steps"].append(step)
            if step["status"] != "passed":
                raise RuntimeError(f"{name} failed: {step['message']}")

        restore_selection(state)
        save_scene(args.checkpoint)
        marker = capture.set_stage("Checkpoint reload")
        open_scene(args.checkpoint, miblend)
        restore_selection(state)
        reload_errors = solver_errors(capture.since(marker))
        if reload_errors:
            codes = ", ".join(item["code"] for item in reload_errors)
            raise RuntimeError(f"Checkpoint reload reported {codes}")

        marker = capture.set_stage("Collect Assets")
        result["assets"] = collect_assets()
        asset_list_errors = solver_errors(capture.since(marker))
        if asset_list_errors:
            codes = ", ".join(item["code"] for item in asset_list_errors)
            raise RuntimeError(f"Asset discovery reported {codes}")
        result["status"] = "passed"
    except Exception:
        error = traceback.format_exc()
        result["errors"].append(error)
        annotation("error", "MiBlend core pipeline", error)
        try:
            if bpy.data.filepath:
                save_scene(args.checkpoint)
        except Exception:
            result["errors"].append(
                "Could not save the failure scene:\n" + traceback.format_exc()
            )
    finally:
        result["blender"] = {
            "version": list(bpy.app.version),
            "version_string": bpy.app.version_string,
            "build_hash": bpy.app.build_hash.decode(
                "utf-8", errors="replace"
            ) if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash),
        }
        result["warnings"] = warning_records(capture)
        result["duration_seconds"] = time.perf_counter() - started
    return result


def find_asset(asset_name: str, asset_path: str) -> int:
    import bpy

    items = bpy.context.scene.miblend_properties.assets_properties.asset_items
    for index, item in enumerate(items):
        if (
                item.get("Asset_name", "") == asset_name
                and item.get("File_path", "") == asset_path
        ):
            return index
    raise RuntimeError(f"Compatible asset disappeared from the list: {asset_name}")


def asset_worker(args: argparse.Namespace) -> dict[str, Any]:
    import bpy

    started = time.perf_counter()
    capture = SolverCapture()
    result: dict[str, Any] = {
        "status": "failed",
        "asset_name": args.asset_name,
        "message": "",
        "warnings": [],
    }
    try:
        miblend = enable_miblend(args.source_root, capture)
        open_scene(args.checkpoint, miblend)
        state = selection_state()
        startup_errors = solver_errors(capture.records)
        if startup_errors:
            codes = ", ".join(item["code"] for item in startup_errors)
            raise RuntimeError(f"MiBlend startup reported {codes}")

        restore_selection(state)
        asset_index = find_asset(args.asset_name, args.asset_path)
        bpy.context.scene.miblend_properties.assets_properties.asset_index = asset_index
        step = run_operator_step(
            args.asset_name,
            lambda: bpy.ops.miblend.import_asset(),
            capture,
        )
        if step["status"] != "passed":
            raise RuntimeError(step["message"] or f"{args.asset_name} failed")

        result_scene = (
            args.output_dir
            / "asset-scenes"
            / f"{safe_filename(args.asset_name)}.blend"
        )
        save_scene(result_scene)
        marker = capture.set_stage(f"Reload {args.asset_name}")
        open_scene(result_scene, miblend)
        reload_errors = solver_errors(capture.since(marker))
        if reload_errors:
            codes = ", ".join(item["code"] for item in reload_errors)
            raise RuntimeError(f"Reloading imported asset reported {codes}")
        result["result_scene"] = str(result_scene)
        result["status"] = "passed"
    except Exception:
        result["message"] = traceback.format_exc()
        annotation("error", f"Asset failed: {args.asset_name}", result["message"])
        try:
            failure_path = (
                args.output_dir
                / "failures"
                / f"{safe_filename(args.asset_name)}.blend"
            )
            save_scene(failure_path)
            result["failure_scene"] = str(failure_path)
        except Exception:
            result["message"] += (
                "\nCould not save the asset failure scene:\n" + traceback.format_exc()
            )
    finally:
        result["warnings"] = warning_records(capture)
        result["duration_seconds"] = time.perf_counter() - started
    return result


def worker_main(args: argparse.Namespace) -> int:
    result: dict[str, Any]
    try:
        if args.result is None:
            raise RuntimeError("Worker result path was not provided")
        if args.worker == "core":
            if args.checkpoint is None:
                raise RuntimeError("Core checkpoint path was not provided")
            result = core_worker(args)
        else:
            if not args.asset_name or args.checkpoint is None:
                raise RuntimeError("Asset worker arguments are incomplete")
            result = asset_worker(args)
    except Exception:
        result = {
            "status": "failed",
            "asset_name": args.asset_name,
            "message": traceback.format_exc(),
            "errors": [traceback.format_exc()],
            "warnings": [],
            "duration_seconds": 0.0,
        }
    if args.result is not None:
        write_json(args.result, result)
    return 0


def main() -> int:
    if "bpy" in sys.modules or "--" in sys.argv:
        return worker_main(parse_arguments(blender_arguments()))
    return orchestrate(parse_arguments(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
