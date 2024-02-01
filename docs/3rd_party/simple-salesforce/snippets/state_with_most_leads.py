from typing import Optional

from simple_salesforce import Salesforce


def connect_to_salesforce(username, password, security_token) -> Salesforce:
    """
    Connects to Salesforce using provided credentials.

    Args:
        username (str): Salesforce username.
        password (str): Salesforce password.
        security_token (str): Salesforce security token.

    Returns:
        Salesforce: Salesforce connection object.
    """
    return Salesforce(
        username=username, password=password, security_token=security_token
    )


def get_state_with_most_leads(sf) -> Optional[str]:
    """
    Retrieves the state with the most leads from Salesforce.

    Args:
        sf (Salesforce): Salesforce connection object.

    Returns:
        str: State with the most leads.
    """
    result = sf.query(
        "SELECT State, COUNT(Id) FROM Lead GROUP BY State ORDER BY COUNT(Id) DESC LIMIT 1"
    )

    if result["records"]:
        return result["records"][0]["State"]
