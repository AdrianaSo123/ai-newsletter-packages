"""Infrastructure facade.

The canonical HTTP implementation lives in `crunchbase_intel.infrastructure.http_fetcher`.
"""

from .domain.errors import FetchError as CrunchbaseFetchError  # noqa: F401
from .infrastructure.http_fetcher import PoliteHttpFetcher as PoliteFetcher  # noqa: F401
