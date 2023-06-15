import argparse
import os
from typing import TYPE_CHECKING

from bounce_challenge.scraper.base import default_vars
from bounce_challenge.scraper.base.auth_method import AuthMethodToken
from bounce_challenge.scraper.utils.scraper_utils import \
    find_scraper_class_by_name

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Type

    from bounce_challenge.scraper.base.scraper import BaseScraper


def main():
    """Starts the Scraper generating process.

    Responsibilities:
    1- Parse & validate the associated command parameters
    2- Retrieve the associated Scraper class
    3- Initialize the Scraper instance and start the scraping process

    Raises
    ------
    ValueError
        Auth Token has been requested but the associated environment variable,
        AUTH_TOKEN could not be retrieved or was empty.
    """
    command_parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="main_parser",
        description="Parses the provided entrypoint arguments"
    )

    command_parser.add_argument("-s", "--scraper_name", type=str, required=True,
                                help="The name of the scraper instance to initialize")
    command_parser.add_argument(
        "-u", "--user_name", type=str, required=True, help="The username to scrape")
    command_parser.add_argument("-o", "--output_path", type=str, required=True,
                                help="The local filesystem path in which to store the data")
    command_parser.add_argument("-t", "--use_token", required=False,
                                action="store_true", help="Should an authentication token be used")
    command_parser.add_argument('-f', '--filters_list', type=list,
                                required=False, nargs='+', help='The list of filters to use')

    parsed_args: argparse.Namespace = command_parser.parse_args()

    # fetch the associated arguments provided on input
    scraper_name: str = parsed_args.scraper_name
    user_name: str = parsed_args.user_name
    is_auth_use_token: bool = parsed_args.use_token
    output_path: str = parsed_args.output_path
    filters_list: List[str] = parsed_args.filters_list

    # retrieve the class type for the corresponding scraper name
    scraper_instance: Type[BaseScraper] = find_scraper_class_by_name(
        scraper_name=scraper_name)

    # hold an instance of an auth method should one be requested
    auth_method: Optional[AuthMethodToken] = None

    # if an auth token request is passed, attempt to retrieve it from the environment variables
    if is_auth_use_token:
        auth_token: str = os.getenv("AUTH_TOKEN")

        if not auth_token:
            raise ValueError(
                "Could not retrieve AUTH_TOKEN from environment variables")

        auth_method: AuthMethodToken = AuthMethodToken(token=auth_token)

    # create a dictionary of arguments to be unpacked and injected into the modular scraper
    scraper_args: Dict[str, Any] = {
        "user": user_name,
        "output_path": output_path,
        "data_filters": filters_list if filters_list else default_vars.default_data_filters
    }

    # create an instance of the target scraper class
    scraper: Type[BaseScraper] = scraper_instance(auth_method=auth_method)
    # initialize the scraping process
    scraper.start(**scraper_args)


if __name__ == "__main__":
    main()
