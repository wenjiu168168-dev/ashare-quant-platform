import importlib
import subprocess
import sys

PROVIDER_IMPORT_ORDERS = [
    [
        "ashare_quant",
        "ashare_quant.data",
        "ashare_quant.data.provider.base",
        "ashare_quant.data.provider.registry",
        "ashare_quant.data.provider.exceptions",
        "ashare_quant.data.provider.capabilities",
        "ashare_quant.data.provider.types",
    ],
    [
        "ashare_quant.data.provider.exceptions",
        "ashare_quant.data.provider.types",
        "ashare_quant.data.provider.capabilities",
        "ashare_quant.data.provider.base",
        "ashare_quant.data.provider.registry",
        "ashare_quant.data",
        "ashare_quant",
    ],
    [
        "ashare_quant.data.provider.registry",
        "ashare_quant.data.provider.base",
        "ashare_quant.data.provider.capabilities",
        "ashare_quant.data.provider.exceptions",
        "ashare_quant.data.provider.types",
        "ashare_quant.data",
        "ashare_quant",
    ],
]


def test_provider_modules_import_in_current_process() -> None:
    for module_name in PROVIDER_IMPORT_ORDERS[0]:
        importlib.import_module(module_name)


def test_provider_modules_import_in_independent_orders() -> None:
    for module_names in PROVIDER_IMPORT_ORDERS:
        code = "\n".join(f"import {module_name}" for module_name in module_names)
        result = subprocess.run(
            [sys.executable, "-c", code],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
