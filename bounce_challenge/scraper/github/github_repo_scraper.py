from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from requests import Session
from requests.compat import urljoin

from bounce_challenge.scraper.base.auth_method import AuthMethodToken
from bounce_challenge.scraper.base.data_accumulator import (DataAccumulator,
                                                            DataOutputType)
from bounce_challenge.scraper.base.error import ScraperError
from bounce_challenge.scraper.base.scraper import BaseScraper

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Type

    from requests import Response


class GithubRepoScraper(BaseScraper):

    _API_URL = 'https://api.github.com'
    _USER_REPOSITORIES_URL: str = "search/repositories?q=user:{username}"
    _SCRAPER_NAME: str = "github_repo_scraper"

    def __init__(self, auth_method: Any = None) -> None:
        super().__init__(scraper_name=GithubRepoScraper._SCRAPER_NAME)

        self._auth_method = auth_method

    def start(self, **kwargs) -> bool:
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

        session: Session = self._authenticate(
        ) if self._auth_method is not None else Session()

        github_user: str = kwargs.get("user")
        output_path: str = kwargs.get("output_path")
        data_filters: Optional[List[str]] = kwargs.get("data_filters", [])

        if not github_user:
            raise ValueError("Missing param user")

        if not output_path:
            raise ValueError("Missing output path")

        # generate the Github user profile link
        user_profile_link: str = self._build_user_repository_url(
            user_name=github_user)
        # create a DataAccumulator instance to hold all the extracted information
        data_accumulator: DataAccumulator = DataAccumulator()
        # exhaust all API requests
        self._exhaust_requests(target_url=user_profile_link, session=session,
                               output_callback=data_accumulator.add_json_data)
        # dump the provided information as a CSV
        data_accumulator.dump(
            output_path=output_path, output_type=DataOutputType.CSV, data_filters=data_filters)

        return True

    def _build_user_repository_url(self: Type[BaseScraper], user_name: str) -> str:
        user_repositories_url: str = GithubRepoScraper._USER_REPOSITORIES_URL.format(
            username=user_name)
        user_profile_link: str = urljoin(
            GithubRepoScraper._API_URL, user_repositories_url)

        return user_profile_link

    def _exhaust_requests(self: Type[BaseScraper], target_url: str, session: Session, output_callback: Callable[..., Any] = None) -> Session:
        response: Response = session.get(url=target_url)
        # extract the content containing the data
        url_data = response.content
        # pass the extracted information to the callable
        output_callback(data=json.loads(url_data).get("items"))

        if self._validate_response(response=response):
            next_page_url: str = self._get_next_page(session=session)

            if next_page_url:
                if self._is_valid_url(target_url=next_page_url):
                    self._exhaust_requests(
                        target_url=next_page_url,
                        session=session,
                        output_callback=output_callback
                    )
                else:
                    logging.warning(f"Skipping invalid URL {next_page_url}")

        logging.info("Exhausted all requests")

    def _get_next_page(self: Type[BaseScraper], session: Session) -> Optional[Session]:
        return session if session.headers.get('link') else None

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
        response_code: int = response.status_code

        if response_code < 300:
            return True

        return self._handle_error(error=ScraperError(response_code))

    def _is_valid_url(self: Type[BaseScraper], target_url: str) -> bool:
        """Validates a target link.

        Parameters
        ----------
        target_url : str
            The target link to be validated.

        Returns
        -------
        bool
            True if the URL is valid.
        """
        return target_url is not None

    def _authenticate(self: Type[BaseScraper]) -> Session:
        """Generates an authenticated session based on the defined AuthMethod


        Returns
        -------
        Session
            A Session instance with the injected authenticated headers

        Raises
        ------
        NotImplementedError
            Raises an error should the Authentication method not be implemented for the Scraper at hands
        """
        auth_method: Any = self._auth_method

        if isinstance(auth_method, AuthMethodToken):
            # sessions persist headers between requests
            session: Session = Session()

            # Add Github token
            github_token: str = auth_method.token

            auth_header: Dict[str, str] = {
                'authorization': f"token {github_token}"
            }

            session.headers.update(auth_header)

            return session
        else:
            raise NotImplementedError(
                f"Authentication not implemented for method {auth_method}")

    @classmethod
    def from_json(cls: Type[BaseScraper], json_config: Dict[str, str]) -> Type[BaseScraper]:
        """Generates an instance of the GithubRepoScraper based on the provided JSON imput

        Parameters
        ----------
        cls : Type[GithubRepoScraper]
            The subclass instance to be instantiated
        json_config : Dict[str, str]
            The provided JSON configuratino to instantiate the object

        Returns
        -------
        Type[GithubRepoScraper]
            Ah instantiated object of class GithubRepoScraper
        """
        raise NotImplementedError()
