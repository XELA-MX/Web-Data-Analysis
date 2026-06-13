"""Diccionario de tecnologías: forma canónica -> alias que la representan.

Empezamos con regex/diccionario (MVP). Camino de evolución: spaCy/embeddings.
Las claves son la forma normalizada que se guarda en jobs.tech_stack; los valores
son los alias (en minúscula) que se buscan en tags + título + descripción.
"""

TECH_ALIASES: dict[str, list[str]] = {
    # Lenguajes
    "python": ["python"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "go": ["golang", "go"],
    "rust": ["rust"],
    "java": ["java"],
    "kotlin": ["kotlin"],
    # Nota: no incluimos "c" a secas como alias: una sola letra genera demasiados
    # falsos positivos (RemoteOK tiene un tag literal "c"). Sí c++ y c#.
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp"],
    "php": ["php"],
    "ruby": ["ruby"],
    "swift": ["swift"],
    "scala": ["scala"],
    "elixir": ["elixir"],
    "sql": ["sql"],
    # Frontend
    "react": ["react", "reactjs", "react.js"],
    "vue": ["vue", "vuejs", "vue.js"],
    "angular": ["angular", "angularjs"],
    "svelte": ["svelte", "sveltekit"],
    "nextjs": ["next.js", "nextjs"],
    "tailwind": ["tailwind", "tailwindcss"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    # Backend / runtime
    "nodejs": ["node.js", "nodejs", "node"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "rails": ["rails", "ruby on rails"],
    "spring": ["spring", "spring boot"],
    "dotnet": [".net", "dotnet", "asp.net"],
    "laravel": ["laravel"],
    "express": ["express", "express.js"],
    "graphql": ["graphql"],
    # Datos / DB
    "postgres": ["postgres", "postgresql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "elasticsearch": ["elasticsearch", "elastic"],
    "kafka": ["kafka"],
    "spark": ["spark"],
    "pandas": ["pandas"],
    # Cloud / infra / DevOps
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud"],
    "azure": ["azure"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],
    "linux": ["linux"],
    "git": ["git"],
    "ci/cd": ["ci/cd", "cicd"],
    # ML / IA
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "machine learning": ["machine learning", "ml"],
}
