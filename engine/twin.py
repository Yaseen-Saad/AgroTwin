# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Twin experiment: does the weighted interval actually cover the truth?

Agent 4 implements the experiment; Agent 7 runs it and records results only in
``qa/REPORT.md``. For every historical window taken as truth, generate synthetic Scout-like
readings, run fusion on the remaining windows, and check whether the truth falls inside the
weighted 10th-90th profit interval. An honest 80% interval should cover about 80% of years; the
report also includes the interval-width ratio and ESS distribution.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any


def run_twin(
    *,
    site: Mapping[str, Any],
    rotations: Sequence[Mapping[str, Any]],
    campaign: Mapping[str, Any],
    seed: int = 0,
) -> dict[str, Any]:
    """Return coverage, width ratio, ESS samples and the assumptions used."""
    raise NotImplementedError("Agent 4: implement Agent guide §5.4")


def main() -> int:
    """Print an honest ``not_run`` status until the experiment is implemented."""
    print(
        json.dumps(
            {
                "status": "not_run",
                "reason": "Agent 4 has not implemented engine.twin.run_twin yet",
                "owner": "Agent 4 (fusion and checks)",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
