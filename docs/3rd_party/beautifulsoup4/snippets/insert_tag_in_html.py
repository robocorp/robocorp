from bs4 import BeautifulSoup

html = """
<!DOCTYPE html>
    <head>
        <title>My page</title>
    </head>
    <body>
        <p class="title"><b>My page</b></p>
        <p class="story">My sisters:
            <a href="http://example.com/maria" class="sister" id="link1">Maria</a>
            <a href="http://example.com/diana" class="sister" id="link2">Diana</a>
        </p>
    </body>
</html>
"""


def insert_sister(html: str, name: str) -> BeautifulSoup:
    """
    Inserts a new a tag in the html document, representing a new sister.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Find the <p> tag with class "story"
    story_paragraph = soup.find("p", class_="story")
    last_a_tag = story_paragraph.find_all("a")[-1]

    new_link_id = int(last_a_tag["id"][-1]) + 1

    # Create a new sister link
    new_sister_link = soup.new_tag(
        "a", href=f"http://example.com/{name}", class_="sister", id=f"link{new_link_id}"
    )
    new_sister_link.string = name.capitalize()

    space_string = soup.new_string(" ")
    # Insert the space and the new sister link before the last <a> tag in the story paragraph
    last_a_tag.insert_after(space_string)
    space_string.insert_after(new_sister_link)

    return soup
