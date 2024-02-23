from typing import Optional

from simple_salesforce import Salesforce


def connect_to_salesforce(
    username: str, password: str, security_token: str
) -> Salesforce:
    """
    Connects to Salesforce using provided credentials.

    Args:
        username: Salesforce username.
        password: Salesforce password.
        security_token: Salesforce security token.

    Returns:
        Salesforce connection object.
    """
    return Salesforce(
        username=username, password=password, security_token=security_token
    )


def get_state_with_most_leads(sf: Salesforce) -> Optional[str]:
    """
    Retrieves the state with the most leads from Salesforce.

    Args:
        sf: Salesforce connection object.

    Returns:
        State with the most leads.
    """
    result = sf.query(
        "SELECT State, COUNT(Id) FROM Lead GROUP BY State ORDER BY COUNT(Id) DESC LIMIT 1"
    )

    if result["records"]:
        return result["records"][0]["State"]
