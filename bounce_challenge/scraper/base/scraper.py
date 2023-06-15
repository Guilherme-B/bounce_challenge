# enable self-referencing type hints
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from bounce_challenge.scraper.base.error import ScraperError

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Type

    from requests import Response


class BaseScraper(ABC):
    """Represents an abstract class for objects related with the Scraper class
    """

    def __init__(self, scraper_name: str) -> None:
        """Instantiates an instance of the abstract class Scraper

        Parameters
        ----------
        scraper_name : str
            The associated scraper name

        Returns
        -------
        Type[Scraper]
            An instance of Scraper
        """
        self._name = scraper_name

    @abstractmethod
    def start(self: Type[BaseScraper], **kwargs) -> bool:
        """Initiates the process of scraping.
            The method triggers the entire process on its own, being responsible for:
            1- (Optional) Authenticating
            2- Downloading the provided information
            3- Filtering the downloaded data
            4- Storing the downloaded data

        Parameters
        ----------
        kwargs : Dict[str, Any]
            The list of kwargs to be passed onto the scraper.

        Returns
        -------
        bool
            True if the process is succesful.
        """

        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_json(cls: Type[BaseScraper], json_config: Dict[str, str]) -> Type[BaseScraper]:
        """Generates an instance of the Scraper subclass based on the provided JSON imput

        Parameters
        ----------
        cls : Type[BaseScraper]
            The subclass instance to be instantiated
        json_config : Dict[str, str]
            The provided JSON configuratino to instantiate the object

        Returns
        -------
        Type[BaseScraper]
            _description_
        """
        raise NotImplementedError()

    @abstractmethod
    def _is_valid_url(self: Type[BaseScraper], target_url: str) -> bool:
        """Validates a target url.

        Parameters
        ----------
        target_url : str
            The target link to be validated.

        Returns
        -------
        bool
            True if the URL is valid.
        """
        raise NotImplementedError()

    @abstractmethod
    def _validate_response(self: Type[BaseScraper], response: Response) -> bool:
        """Validates the provided request response based on its status code

        Parameters
        ----------
        response : Response
            The Response instance to be validated

        Returns
        -------
        bool
            True if the response is valid
        """
        raise NotImplementedError()

    def _handle_error(self: Type[BaseScraper], error: ScraperError, callback: Callable[..., Any] = None) -> None:
        """Handles any response errors triggered during the scraping process.

        Raises
        ------
        ValueError
            Raises a value error if an uncaught error is triggered
        """
        match error:
            case ScraperError.UNAUTHORIZED:
                logging.error("Unable to access authenticated page")
            case _:
                pass

        if callback:
            # call the associated callback function
            callback()

        raise ValueError(f"Aborting due to error received: {error}")

    @property
    def name(self: Type[BaseScraper]) -> str:
        """Returns the scraper class' name


        Returns
        -------
        str
            The scraper's name
        """
        return self._name
