"""Re-export the consolidated SQLAlchemy models from the sibling models.py file."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_MODELS_PATH = Path(__file__).resolve().parents[1] / "models.py"
_SPEC = spec_from_file_location("app._flat_models", _MODELS_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load models from {_MODELS_PATH}")

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

for _name in dir(_MODULE):
    if _name.startswith("_"):
        continue
    globals()[_name] = getattr(_MODULE, _name)

__all__ = [name for name in globals() if not name.startswith("_")]
