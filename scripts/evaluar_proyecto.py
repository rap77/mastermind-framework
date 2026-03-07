#!/usr/bin/env python3
"""
MasterMind Framework - Evaluador de Proyectos Externos

Uso:
    python evaluar_proyecto.py                    # Usa el brief de ejemplo
    python evaluar_proyecto.py --brief "tu texto" # Brief inline
    python evaluar_proyecto.py --file brief.md    # Brief desde archivo
    python evaluar_proyecto.py --mcp              # Usa NotebookLM real (requiere nlm CLI)
"""
import logging
import sys
import os
import argparse

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Add mastermind-cli to path
MASTERMIND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{MASTERMIND_ROOT}/tools/mastermind-cli")

from mastermind_cli.orchestrator import Coordinator, OutputFormatter


# Brief de ejemplo
EJEMPLO_BRIEF = """
Una app de productividad para freelancers.

PROBLEMA:
Los freelancers trabajan en múltiples proyectos con diferentes clientes
y les es difícil organizar su tiempo, trackear horas, y manejar facturas.
Usan herramientas separadas (calendar, timesheet, invoicing) que no
se integran bien.

SOLUCIÓN:
App all-in-one que combina:
- Time tracking con inicio/stop de tareas
- Calendar integrado con deadlines
- Invoicing automático basado en horas trackeadas
- Client management con historial de proyectos

USUARIO OBJETIVO:
Freelancers independientes (designers, developers, writers) que trabajan
con 3-10 clientes activos mensualmente.

EVIDENCIA:
- Entrevisté 12 freelancers, 10 dicen que "organizar el tiempo" es top pain
- 8 usan spreadsheets manuales para tracking
- 6 pagan por 2+ herramientas (timesheet + invoicing)
- Todos estarían dispuestos a pagar $15-30/mes por una solución integrada

MÉTRICAS OBJETIVO:
- D7 retention: >25%
- D30 retention: >15%
- Weekly active users: >40% de registrados
- Paid conversion: >5% de activos
- NPS: >30

MODELO DE MONETIZACIÓN:
Freemium:
- Free: 3 clientes activos, 10 invoices/mes
- Pro: $15/mes - clientes ilimitados, invoices ilimitadas
- Business: $30/mes - team collaboration, reports
"""


BRIEF_TEMPLATE = """
[PROYECTO A EVALUAR]

PROBLEMA:
¿Qué dolor resuelve tu producto? Sé específico.

SOLUCIÓN:
¿Cómo lo resuelves? Evita términos genéricos.

USUARIO OBJETIVO:
¿Quién es tu usuario? Qué problemas tiene.

EVIDENCIA:
¿Cómo validaste este problema?
- Entrevistas realizadas
- Datos de mercado
- Comportamiento observado

MÉTRICAS OBJETIVO:
- Retention (D7, D30)
- Activation rate
- NPS o satisfacción
- Conversión a pago (si aplica)

MODELO DE MONETIZACIÓN (si aplica):
Freemium, pago, enterprise, etc.
"""


def print_header(text: str) -> None:
    """Print a formatted section header to the log.

    Args:
        text: Header text to display.
    """
    logger.info("\n" + "=" * 70)
    logger.info(text)
    logger.info("=" * 70)


def evaluar_brief(brief: str, use_mcp: bool = False, flow: str = "validation_only") -> dict:
    """Evalúa un brief usando el MasterMind Framework.

    Args:
        brief: Brief text in Markdown or plain text format.
        use_mcp: Whether to use MCP integration for real NotebookLM queries.
        flow: Flow type to use (validation_only, full_product, optimization).

    Returns:
        Dictionary with evaluation results including score, feedback, and recommendations.
    """

    print_header("🧠 MENTE MAESTRA - Evaluación de Proyecto")

    logger.info(f"\n📝 BRIEF:")
    logger.info("-" * 70)
    logger.info(brief[:500] + "..." if len(brief) > 500 else brief)
    logger.info("-" * 70)

    logger.info(f"\n🔄 Flow: {flow}")
    logger.info(f"🔌 MCP: {'enabled (NotebookLM real)' if use_mcp else 'disabled (modo simulación)'}")

    formatter = OutputFormatter()
    coordinator = Coordinator(formatter=formatter, use_mcp=use_mcp)

    result = coordinator.orchestrate(
        brief=brief.strip(),
        flow=flow,
        max_iterations=3
    )

    print_header("📊 RESULTADO")

    logger.info(f"\nStatus: {result.get('status')}")
    logger.info(f"Veredicto Final: {result.get('veredict')}")
    logger.info(f"Iteraciones: {result.get('iterations', 1)}")

    if result.get('plan'):
        logger.info(f"\n📋 Plan de Ejecución:")
        logger.info(result['plan'])

    if result.get('evaluations'):
        logger.info(f"\n🧠 Evaluaciones por Cerebro:")
        for i, eval_result in enumerate(result['evaluations'], 1):
            brain_name = eval_result.get('brain_id', 'Unknown')
            score = eval_result.get('score', 'N/A')
            logger.info(f"\n  [{i}] {brain_name}")
            logger.info(f"      Score: {score}")

    if result.get('veredict') == 'REJECT':
        logger.info("\n❌ El brief fue RECHAZADO.")
        logger.info("   Revisa: evidencia insuficiente, métricas poco realistas, o problema poco claro.")
    elif result.get('veredict') == 'CONDITIONAL':
        logger.info("\n⚠️  Elbrief fue ACEPTADO CONDICIONALMENTE.")
        logger.info("   Necesita: más evidencia, métricas más ambiciosas, o clarificar la propuesta.")
    elif result.get('veredict') == 'APPROVE':
        logger.info("\n✅ El brief fue APROBADO.")
        logger.info("   Buen trabajo: problema claro, evidencia sólida, métricas realistas.")

    return result


def main() -> None:
    """Entry point for the MasterMind project evaluator."""
    parser = argparse.ArgumentParser(
        description="Evalúa proyectos usando el MasterMind Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=BRIEF_TEMPLATE
    )
    parser.add_argument(
        '--brief', '-b',
        type=str,
        help='Brief del proyecto (texto inline)'
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Archivo con el brief (.md o .txt)'
    )
    parser.add_argument(
        '--mcp',
        action='store_true',
        help='Usar MCP (NotebookLM real) en lugar de simulación'
    )
    parser.add_argument(
        '--flow',
        type=str,
        choices=['validation_only', 'full_product', 'optimization', 'technical_review'],
        default='validation_only',
        help='Tipo de flujo (default: validation_only)'
    )
    parser.add_argument(
        '--example',
        action='store_true',
        help='Usar el brief de ejemplo (freelancers app)'
    )

    args = parser.parse_args()

    # Determinar el brief a usar
    if args.example:
        brief = EJEMPLO_BRIEF
    elif args.file:
        with open(args.file, 'r') as f:
            brief = f.read()
    elif args.brief:
        brief = args.brief
    else:
        # Si no se proporciona nada, usar el ejemplo
        logger.info("⚠️  No se proporcionó brief. Usando ejemplo.")
        brief = EJEMPLO_BRIEF

    # Evaluar
    result = evaluar_brief(
        brief=brief,
        use_mcp=args.mcp,
        flow=args.flow
    )

    # Exit code basado en veredicto
    if result.get('veredict') == 'APPROVE':
        sys.exit(0)
    elif result.get('veredict') == 'CONDITIONAL':
        sys.exit(1)
    else:  # REJECT
        sys.exit(2)


if __name__ == "__main__":
    main()
