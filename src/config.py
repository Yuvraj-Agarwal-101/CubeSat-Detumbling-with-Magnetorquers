"""Public compatibility imports and case summary command."""

from .inputs.case import (
    BASELINE, SCHEMA, case_summary, initial_state, load_config, main,
    runtime_config, solver_settings, validate_config,
)

__all__ = ["BASELINE", "SCHEMA", "case_summary", "initial_state", "load_config",
           "runtime_config", "solver_settings", "validate_config"]

if __name__ == "__main__":
    main()
