# processor (Python)

Limpia y enriquece los `RawJob` → `Job`. El procesador es la pieza **"inteligente"**.

- Extrae `tech_stack` (diccionario de tecnologías + regex; luego spaCy si interesa).
- Normaliza salario a `(min, max, currency)`.
- Infiere `seniority` y detecta `remote`.
- Deduplica por `fingerprint`.

> **Estado:** scaffold (Fase 0). La implementación empieza en la **Fase 2**. Ver
> [`documentación/V1/05-roadmap.md`](../documentación/V1/05-roadmap.md).
