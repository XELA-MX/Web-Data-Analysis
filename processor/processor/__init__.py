"""Procesador del Tech Job Market Analyzer.

Lee ofertas crudas de `raw_jobs`, las limpia y enriquece (tech_stack, salario,
seniority, remoto, fingerprint) y las escribe en `jobs`. Es la pieza "inteligente"
del pipeline; el scraper (Go) solo recoge. Ver documentación/V1/02-arquitectura.md.
"""

__all__ = ["pipeline", "extract", "db", "tech_dictionary"]
