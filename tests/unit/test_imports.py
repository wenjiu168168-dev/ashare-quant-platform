import importlib
import subprocess
import sys

MODULE_IMPORT_ORDERS = [
    [
        "ashare_quant",
        "ashare_quant.config.settings",
        "ashare_quant.utils.exceptions",
        "ashare_quant.utils.logging",
    ],
    [
        "ashare_quant.utils.exceptions",
        "ashare_quant",
        "ashare_quant.utils.logging",
        "ashare_quant.config.settings",
    ],
    [
        "ashare_quant.utils.logging",
        "ashare_quant.config.settings",
        "ashare_quant.utils.exceptions",
        "ashare_quant",
    ],
]


def test_core_modules_import_in_current_process() -> None:
    for module_name in MODULE_IMPORT_ORDERS[0]:
        importlib.import_module(module_name)


def test_core_modules_import_in_independent_orders() -> None:
    for module_names in MODULE_IMPORT_ORDERS:
        code = "\n".join(f"import {module_name}" for module_name in module_names)
        result = subprocess.run(
            [sys.executable, "-c", code],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
