from __future__ import annotations

from enum import Enum, unique
from typing import TYPE_CHECKING

from bounce_challenge.scraper.github.github_repo_scraper import \
    GithubRepoScraper

if TYPE_CHECKING:
    from typing import Type

    from bounce_challenge.scraper.base.scraper import BaseScraper


@unique
class ScraperTypes(Enum):
    """
        Represents the list of available scrapers and the corresponding input var
    """
    GITHUB_REPOSITORIES = "github_repositories"


def find_scraper_class_by_name(scraper_name: str) -> Type[BaseScraper]:
    """Returns a subclass of BaseScraper with the corresponding scraper name

    Returns
    -------
    Type[BaseScraper]
        A subclass of BaseScraper

    Raises
    ------
    NotImplementedError
        When the provided scraper name does not exist
    """
    scraper_type: ScraperTypes = ScraperTypes(scraper_name)
    scraper_instance: Type[BaseScraper] = None

    match scraper_type:
        case ScraperTypes.GITHUB_REPOSITORIES:
            scraper_instance = GithubRepoScraper
        case _:
            raise NotImplementedError(
                f"Provided scraper not implemented: {scraper_name}")

    match scraper_type:
        case ScraperTypes.GITHUB_REPOSITORIES:
            scraper_instance = GithubRepoScraper
        case _:
            raise NotImplementedError(
                f"Provided scraper not implemented: {scraper_name}")

    return scraper_instance
