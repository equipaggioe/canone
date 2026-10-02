"""The tables, one module per model in a package per domain.

Importing this package imports every model, so ``Base.metadata``
holds every table.
"""

import importlib
import pkgutil

for module in pkgutil.walk_packages(__path__, f"{__name__}."):
    importlib.import_module(module.name)
