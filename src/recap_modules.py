import os
from pathlib import Path
from typing import List, Dict


def is_recap_module(module: str) -> bool:
    try:
        module = __import__(module)
        return (hasattr(module, 'recap_module_name') and
                hasattr(module, 'main'))
    except Exception:
        return False


def get_local_modules() -> List[str]:
    modules = []

    search_dir = Path(__file__).resolve().parent

    for (p, _, files) in os.walk(search_dir):
        if '__init__.py' in files:
            modules.append(os.path.basename(p))

    return modules


def get_recap_modules() -> Dict:
    modules = filter(is_recap_module, get_local_modules())
    recap_modules = {}
    for m in modules:
        module = __import__(m)
        command = getattr(module, 'recap_module_name')
        recap_modules[command] = module
    return recap_modules
