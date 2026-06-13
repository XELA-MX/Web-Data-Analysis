"""Entrypoint del procesador.

Uso:
    python -m processor                 # procesa todo lo pendiente
    python -m processor --batch-size 200
"""

from __future__ import annotations

import argparse
import logging
import sys

from . import pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Procesa raw_jobs -> jobs")
    parser.add_argument("--batch-size", type=int, default=500, help="ofertas por lote")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    try:
        pipeline.run(batch_size=args.batch_size)
    except Exception:
        logging.getLogger("processor").exception("fallo en el procesado")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
