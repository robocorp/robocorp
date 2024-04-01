# Beautifulsoup4

Beautiful Soup is a Python library specialized for pulling data out of HTML and XML files.

At some extent it can be used to modify the HTML as well.

## Usage

```python
from bs4 import BeautifulSoup

html = """
<!DOCTYPE html>
    <head>
        <title>My page</title>
    </head>
    <body>
        <p class="title"><b>My page</b></p>
        <p class="story">My sisters:
            <a href="http://example.com/maria" class="sister" id="link1">Maria</a>,
            <a href="http://example.com/diana" class="sister" id="link2">Diana</a> and
        </p>
    </body>
</html>
"""

soup = BeautifulSoup(html, 'html.parser')

# find all links in the HTML and print their href attributes
for link in soup.find_all('a'):
    print(link.get('href'))
```

> AI/LLM's are quite good with `beautifulsoup4`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Insert a new tag in html](snippets/insert_tag_in_html.py)

## Links and references

- [PyPI](https://pypi.org/project/beautifulsoup4/)
- [Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
