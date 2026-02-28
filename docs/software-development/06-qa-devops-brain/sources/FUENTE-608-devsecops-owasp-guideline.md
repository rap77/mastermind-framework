---
source_id: "FUENTE-608"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "OWASP DevSecOps Guideline: Integrating Security into the DevOps Pipeline"
author: "OWASP Foundation (Community)"
expert_id: "EXP-608"
type: "guide"
language: "en"
year: 2023
url: "https://owasp.org/www-project-devsecops-guideline/"
skills_covered: ["H9"]
distillation_date: "2026-02-27"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.1.0"
last_updated: "2026-02-27"
changelog:
  - version: "1.1.0"
    date: "2026-02-27"
    changes:
      - "Cargada en NotebookLM (notebook ID: 74cd3a81-1350-4927-af14-c0c4fca41a8e)"
  - version: "1.0.0"
    date: "2026-02-27"
    changes:
      - "Ficha creada para cubrir GAP de DevSecOps y seguridad en el pipeline"
      - "Formato estándar del MasterMind Framework"
status: "active"

habilidad_primaria: "DevSecOps: integración de seguridad en el pipeline de CI/CD desde el diseño"
habilidad_secundaria: "SAST, DAST, dependency scanning, secrets management y threat modeling"
capa: 2
capa_nombre: "Frameworks"
relevancia: "CRÍTICA — Cubre el GAP de seguridad en el pipeline. Las fuentes base mencionan 'shift-left security' pero ninguna explica cómo implementarlo. Esta guía define exactamente qué herramientas y procesos integrar en cada stage del pipeline para que la seguridad sea automática, no manual."
gap_que_cubre: "DevSecOps, SAST/DAST, secrets management, threat modeling en el pipeline — no cubierto por ninguna de las 5 fuentes base"
---

# FUENTE-608: OWASP DevSecOps Guideline

## Tesis Central

> La seguridad no puede ser un checkpoint al final del pipeline ni responsabilidad exclusiva de un equipo de seguridad separado: debe integrarse en cada stage del desarrollo como controles automáticos que el equipo de ingeniería ejecuta sin friccción. Cuando la seguridad se hace manualmente y al final, siempre pierde contra la presión de entregar features. Cuando es automática y temprana, deja de ser un obstáculo para convertirse en una red de seguridad.

---

## 1. Principios Fundamentales

> **P1: Shift-left security — la seguridad empieza en el diseño, no en el deploy**
> Cada vulnerabilidad detectada en producción cuesta órdenes de magnitud más que una detectada en el diseño. El shift-left no es solo mover las herramientas más a la izquierda en el pipeline: es incluir consideraciones de seguridad en el threat modeling, en los criterios de aceptación de las historias, y en el code review.
> *Contexto: Al hacer el refinement de una historia de usuario que involucra autenticación, datos sensibles, o integración con sistemas externos, preguntar: ¿qué puede salir mal desde el punto de vista de seguridad? Los criterios de aceptación deben incluir los escenarios de seguridad.*

> **P2: Security as Code — las políticas de seguridad se definen en código y se ejecutan automáticamente**
> Una política de seguridad escrita en un documento PDF que alguien debe leer y aplicar manualmente no es una política: es una recomendación. Una política de seguridad implementada como un check automático en el pipeline que falla el build si no se cumple, sí lo es.
> *Contexto: Aplicar a todas las políticas de seguridad: "todas las imágenes Docker deben escanearse con Trivy" → step obligatorio en el pipeline. "No se permiten credenciales en el código" → pre-commit hook + SAST en el pipeline.*

> **P3: El equipo de seguridad como habilitador, no como gatekeeper**
> En el modelo tradicional, el equipo de seguridad aprueba o rechaza releases. Este modelo no escala y genera confrontación. En DevSecOps, el equipo de seguridad define las políticas, construye las herramientas que automatizan los checks, y entrena a los developers para que puedan aplicarlas independientemente.
> *Contexto: El KPI correcto del equipo de seguridad no es "vulnerabilidades encontradas" sino "vulnerabilidades encontradas automáticamente en el pipeline antes de producción."*

> **P4: Los secretos nunca van en el código, nunca en el repositorio**
> Un secreto (contraseña, API key, token) commiteado a un repositorio de Git debe considerarse comprometido, aunque se borre inmediatamente. Git guarda el historial completo: el secreto está en el historial aunque ya no esté en el código actual.
> *Contexto: Si se descubre un secreto en el repo, la respuesta no es borrarlo y hacer commit: es rotar la credencial inmediatamente (asumir que está comprometida) y después limpiar el historial de Git si es necesario.*

> **P5: Las dependencias de terceros son parte de la superficie de ataque**
> Un proyecto moderno tiene cientos de dependencias (npm, pip, maven). Cada dependencia con una vulnerabilidad conocida es un vector de ataque. La gestión de dependencias no es solo actualizar versiones: es monitorear continuamente si las dependencias actuales tienen CVEs nuevas.
> *Contexto: El dependency scanning automático en el pipeline no es opcional. Las vulnerabilidades de terceros (Log4Shell, etc.) se descubren frecuentemente y el equipo debe enterarse antes de que lleguen a producción, no después.*

---

## 2. Frameworks y Metodologías

### Framework 1: El Pipeline de Seguridad — Qué herramienta en qué stage

**Propósito:** Definir exactamente qué controles de seguridad automáticos van en cada stage del pipeline de CI/CD.
**Cuándo usar:** Al construir o auditar el pipeline de CI/CD de un proyecto. Al hacer un threat model de la pipeline de seguridad.

**Stage 0 — Pre-commit (en el equipo del developer, antes de hacer commit):**
- **Pre-commit hooks:** Detectan secrets en el código antes de que lleguen al repositorio
- Herramientas: `git-secrets`, `detect-secrets`, `gitleaks`
- Configuración: el hook falla si detecta patrones de API keys, tokens, o contraseñas
- Importante: es una red de seguridad, no el único control. Los secrets management deben usarse desde el diseño.

**Stage 1 — Commit Stage (cada commit, < 10 minutos):**
- **SAST (Static Application Security Testing):** Analiza el código fuente buscando vulnerabilidades conocidas
  - Herramientas: SonarQube, Semgrep, CodeQL (GitHub), Bandit (Python), ESLint security plugins
  - Detecta: SQL injection, XSS potencial, hardcoded secrets, uso de funciones inseguras
- **Dependency scanning:** Verifica si las dependencias tienen CVEs conocidas
  - Herramientas: Snyk, OWASP Dependency-Check, `npm audit`, `pip-audit`
  - Configuración: fallar el build si hay vulnerabilidades CRITICAL o HIGH sin excepción documentada
- **Secrets scanning en el repo:** Por si el pre-commit hook falló
  - Herramientas: GitLeaks, TruffleHog, GitHub Secret Scanning

**Stage 2 — Build y Container Stage:**
- **Container image scanning:** La imagen Docker se escanea antes de publicarse
  - Herramientas: Trivy, Clair, Snyk Container
  - Detecta: paquetes del OS con CVEs, configuraciones inseguras del Dockerfile
  - Configuración: fallar si hay CRITICAL. Alertar (no fallar) en HIGH para no bloquear deploys por falsos positivos.
- **Infrastructure as Code scanning:** El código de Terraform/CloudFormation se escanea
  - Herramientas: Checkov, tfsec, KICS
  - Detecta: buckets S3 públicos, security groups demasiado permisivos, logging desactivado

**Stage 3 — Staging / Integration Stage:**
- **DAST (Dynamic Application Security Testing):** Prueba la aplicación corriendo, simulando ataques
  - Herramientas: OWASP ZAP, Burp Suite (CI mode), Nuclei
  - Detecta: vulnerabilidades que solo se revelan en runtime (injection, autenticación rota, SSRF)
  - Tiempo: 15-30 minutos en modo baseline; varias horas en modo full scan (solo para releases mayores)
- **Penetration testing automatizado básico:** Checks del OWASP Top 10 automáticos

**Stage 4 — Pre-producción (para releases significativas):**
- **Penetration testing manual:** Para features con alta superficie de ataque (autenticación, pagos, datos sensibles)
- **Security review de arquitectura:** Para cambios de infraestructura o nuevas integraciones externas

**Output esperado:** Pipeline con checks de seguridad automáticos en cada stage. El equipo de desarrollo recibe feedback de seguridad en minutos, no en semanas.

---

### Framework 2: Threat Modeling simplificado — STRIDE

**Propósito:** Identificar las amenazas de seguridad de un sistema antes de construirlo, para diseñar los controles apropiados.
**Cuándo usar:** En el design review de cualquier feature nueva que involucre: autenticación, datos sensibles, integraciones externas, o infraestructura nueva.

**STRIDE — Las 6 categorías de amenazas:**

| Amenaza | Descripción | Ejemplo | Control típico |
|---------|-------------|---------|----------------|
| **S**poofing | Suplantar la identidad de un usuario o sistema | Alguien usa el token de otro usuario | Autenticación fuerte, validación de tokens, MFA |
| **T**ampering | Modificar datos en tránsito o en reposo | Modificar un request HTTP para cambiar el monto de un pago | HTTPS obligatorio, firmas digitales, checksums |
| **R**epudiation | Negar haber realizado una acción | "Yo nunca borré ese registro" | Audit logs completos e inmutables |
| **I**nformation Disclosure | Acceder a datos sin autorización | Ver datos de otro usuario por IDOR | Autorización a nivel de objeto, no solo de endpoint |
| **D**enial of Service | Hacer el sistema inaccesible | Flood de requests que agota los recursos | Rate limiting, circuit breakers, auto-scaling |
| **E**levation of Privilege | Obtener permisos que no corresponden | Un usuario normal accede a funciones de admin | Principio de mínimo privilegio, validación de roles en cada acción |

**Proceso simplificado (45-60 minutos por feature):**
1. **Diagramar** el flujo de datos de la feature: actores, sistemas, datos que fluyen
2. **Para cada componente**, preguntar: ¿cómo podría alguien atacar este componente con cada amenaza STRIDE?
3. **Priorizar** las amenazas más probables y de mayor impacto
4. **Definir controles** para las amenazas priorizadas
5. **Documentar** los controles como criterios de aceptación o como tests de seguridad

**Output esperado:** Lista de amenazas identificadas con su prioridad y el control diseñado para mitigarlas. Los controles se convierten en requisitos técnicos de la feature.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Defense in depth** | La seguridad no depende de una sola capa: hay múltiples capas de controles independientes. Si una falla, las otras siguen protegiendo. Un atacante debe comprometer todas las capas para tener éxito. | Al diseñar la seguridad de un sistema, no confiar solo en una medida (ej: "tenemos autenticación, estamos seguros"). Preguntar: ¿qué pasa si la autenticación falla? ¿Si alguien obtiene un token válido? ¿Si comprometen la base de datos? |
| **Attack surface minimization** | La superficie de ataque es el conjunto de puntos donde un atacante puede intentar acceder al sistema. Cuanto más pequeña, mejor. Cada endpoint, cada dependencia, cada puerto abierto es superficie de ataque. | Al revisar un PR que agrega una nueva funcionalidad, preguntar: ¿esto aumenta la superficie de ataque? ¿Es necesario que sea público? ¿Puede limitarse el acceso a IPs específicas o usuarios autorizados? |
| **Fail secure** | Cuando el sistema falla, debe fallar en el estado más seguro posible. Si la validación de autorización falla por un error, el default debe ser denegar acceso, no permitirlo. | Revisar todos los catch/except o try/catch que manejan errores de seguridad: ¿qué hace el código si la validación lanza una excepción? Si el default es "continuar", está fail-open (inseguro). |
| **Principio de mínimo privilegio** | Cada componente, usuario, y servicio debe tener únicamente los permisos que necesita para su función, nada más. Un servicio que solo lee de una tabla no debe tener permisos de escritura ni de borrado. | Auditar los IAM roles y permisos de base de datos de todos los servicios. Es muy común encontrar roles con `*:*` (todos los permisos) que se asignaron "para que funcione rápido" y nadie revisó después. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Vulnerabilidad CRITICAL en una dependencia, sin fix disponible | Mitigar con controles alternativos + plan de reemplazo de la dependencia | Ignorar hasta que haya fix | Una vulnerabilidad CRITICAL sin fix requiere controles compensatorios inmediatos: aislar el componente, aumentar el monitoreo, o desactivar la feature afectada. |
| DAST produce falsos positivos que bloquean el pipeline | Configurar como "alertar" en lugar de "fallar" + revisar semanalmente | Ignorar los falsos positivos | Los falsos positivos que bloquean el pipeline crean incentivos para desactivar el control. Mejor alertar y revisar que fallar y ser ignorado. |
| ¿SAST o DAST primero si solo puedo elegir uno? | SAST primero | DAST | SAST es más rápido, más barato, y se ejecuta sin desplegar la aplicación. Detecta una clase más amplia de problemas. DAST es el complemento para lo que SAST no puede ver. |
| Secreto en el código descubierto en producción | Rotar la credencial inmediatamente (asumir comprometida) | Borrar el commit y hacer push force | La rotación es la acción de seguridad. La limpieza del historial es secundaria y más lenta. El orden importa: primero la seguridad, después la higiene del repo. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Penetration testing solo una vez al año** | El código cambia constantemente. Las vulnerabilidades encontradas en el pentest del año pasado están arregladas, pero las nuevas features del último trimestre nunca se auditaron. El "certificado" de seguridad anual da una falsa sensación de seguridad. | DAST automático en el pipeline para cada release + pentest manual anual para validación profunda de las áreas de mayor riesgo. |
| **Variables de entorno como solución a secretos** | Las variables de entorno en `.env` files o en scripts de deploy no son secretos seguros: son visibles en el proceso, en los logs, y en `docker inspect`. Son mejores que hardcoded pero no son la solución final. | AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault. El servicio fetcha el secreto en runtime con su IAM role, sin que el valor pase por variables de entorno del sistema. |
| **"El equipo de seguridad revisará antes del release"** | El review manual de seguridad como único control crea un cuello de botella masivo. El equipo de seguridad no puede revisar cada PR de cada equipo. El review siempre llega tarde y bajo presión. | Los controles automáticos (SAST, DAST, dependency scanning) corren en cada PR. El equipo de seguridad se enfoca en definir políticas y revisar las excepciones, no en cada cambio. |
| **Ignorar las vulnerabilidades de las dependencias porque "son de terceros"** | El código de terceros corre con los mismos privilegios que el código propio. Una vulnerabilidad en `lodash` o `log4j` es tan peligrosa como una en el código propio. Log4Shell (2021) demostró que las vulnerabilidades de dependencias tienen impacto catastrófico. | Dependency scanning en el pipeline. Política clara: CRITICAL se arregla en 24h, HIGH en 1 semana, MEDIUM en el próximo sprint. Tracking de excepciones documentadas. |
| **Security theater — checks que siempre pasan** | Tener SAST configurado para no reportar ningún problema porque las reglas están tan permisivas que nunca disparan. Da la apariencia de seguridad sin el beneficio. | Configurar las herramientas con reglas razonables y revisarlas periódicamente. Si el SAST nunca encuentra nada en semanas, probablemente las reglas están demasiado laxas o el alcance es demasiado limitado. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Equihax (Capital One breach, 2019) — SSRF y IMDS sin protección

- **Situación:** Capital One sufrió una brecha que expuso datos de 100 millones de clientes. El vector de ataque fue un Server-Side Request Forgery (SSRF) que permitió al atacante hacer requests al Instance Metadata Service (IMDS) de AWS y obtener credenciales temporales de IAM con permisos excesivos.
- **Qué falló:** El firewall de aplicación web estaba mal configurado (SSRF no bloqueado). Las credenciales IAM tenían permisos demasiado amplios (violación de mínimo privilegio). No había detección del acceso inusual al IMDS.
- **Lección de DevSecOps:** Un DAST correctamente configurado habría detectado el SSRF antes de producción. Los IAM roles con mínimo privilegio habrían limitado el daño a los datos que el servicio específico necesitaba, no a 100 millones de registros. La seguridad como afterthought tiene consecuencias masivas.

### Caso 2: Log4Shell (2021) — Dependency scanning como primera línea de defensa

- **Situación:** En diciembre de 2021, se descubrió CVE-2021-44228 en Log4j, una librería de logging usada en prácticamente toda aplicación Java. La vulnerabilidad permitía ejecución remota de código con un simple string en cualquier campo logueado.
- **Qué diferencia al que estaba preparado:** Las organizaciones con dependency scanning automático en el pipeline recibieron una alerta el mismo día de la publicación del CVE. En 24-48 horas tenían el parche aplicado. Las organizaciones sin scanning tardaron semanas en saber si estaban afectadas y cómo.
- **Resultado medido:** Según datos de Qualys, las organizaciones con DevSecOps maduro parchearon Log4Shell en un promedio de 3 días. Las sin DevSecOps: más de 4 semanas. En esas 4 semanas, eran vulnerables a ataques activos masivos.
- **Lección:** El dependency scanning automático no es un nice-to-have. Es la diferencia entre parchear una vulnerabilidad crítica en días vs. semanas de exposición.

### Caso 3: Shopify — Bug Bounty como extensión del DevSecOps

- **Situación:** Shopify procesa billones de dólares en transacciones. La seguridad es crítica. Sin embargo, ningún equipo interno puede encontrar todos los bugs de seguridad.
- **Decisión:** Implementaron un programa de bug bounty (via HackerOne) como complemento a su pipeline de DevSecOps. Los investigadores externos reportan vulnerabilidades a cambio de recompensas económicas.
- **Resultado:** El programa de bug bounty ha pagado más de $1M en recompensas y ha encontrado vulnerabilidades que los controles internos no detectaron. El costo de las recompensas es una fracción del costo de un breach.
- **Lección:** El DevSecOps automático en el pipeline y el testing manual (pentest, bug bounty) son complementarios. Los humanos creativos encuentran vulnerabilidades que la automatización no puede anticipar.

---

## Conexión con el Cerebro #6

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| H9 — DevSecOps y seguridad en el pipeline | Esta fuente es la referencia principal de DevSecOps: qué herramientas usar (SAST, DAST, dependency scanning, secrets scanning), en qué stage del pipeline va cada una, y cómo hacer threat modeling. Cubre el gap completamente. |

---

## Preguntas que el Cerebro puede responder

1. ¿Qué herramientas de seguridad debemos integrar en nuestro pipeline de CI/CD y en qué orden?
2. ¿Cómo gestionamos los secretos y credenciales en nuestra aplicación sin exponerlos en variables de entorno?
3. ¿Tenemos una dependencia con una vulnerabilidad crítica sin fix disponible — qué hacemos?
4. ¿Cómo hacemos un threat model de una feature nueva sin ser expertos en seguridad?
5. ¿Cuál es la diferencia entre SAST y DAST y qué detecta cada uno?
6. ¿Cómo respondemos cuando encontramos un secreto commiteado al repositorio en el pasado?
