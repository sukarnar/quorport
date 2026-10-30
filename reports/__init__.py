"""PDF / HTML report generation for quorport.

Usage (CLI):
    quorport report run <name>            # → <output>.pdf
    quorport report run <name> --html     # → <output>.html (preview)

Requires the 'reports' extra:
    pip install quorport[reports]         # installs jinja2 + weasyprint
"""
from .service import ReportService

__all__ = ["ReportService"]
