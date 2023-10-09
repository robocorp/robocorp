import pytest


class TestMatchObject:
    """Test locator resolver."""

    @pytest.mark.parametrize(
        "locator, locators",
        [
            ("Robocorp", [("name", "Robocorp", 0)]),
            ("Robocorp Window", [("name", "Robocorp Window", 0)]),
            ("name:Robocorp Window", [("name", "Robocorp", 0), ("name", "Window", 0)]),
            ('name:"Robocorp Window"', [("name", "Robocorp Window", 0)]),
            ('name:"Robocorp\'s Window"', [("name", "Robocorp's Window", 0)]),
            (
                'name:"Robocorp\'s Window" class:"My Class"',
                [("name", "Robocorp's Window", 0), ("class", "My Class", 0)],
            ),
            (
                "Robocorp > File",
                [("name", "Robocorp", 0), ("name", "File", 1)],
            ),  # this isn't currently used in end-to-end logic
            (
                (
                    '"Robocorp Window93" subname:Robocorp and class:"My Class" '
                    "Test regex:Robo.+"
                ),
                [
                    ("name", "Robocorp Window93", 0),
                    ("subname", "Robocorp", 0),
                    ("class", "My Class", 0),
                    ("name", "Test", 0),
                    ("regex", "Robo.+", 0),
                ],
            ),
            ("Robocorp:Window", [("name", "Robocorp:Window", 0)]),
            ("name:Robocorp:Window", [("name", "Robocorp:Window", 0)]),
            (
                "Robocorp:Window class:Class",
                [("name", "Robocorp:Window", 0), ("class", "Class", 0)],
            ),
            (
                "Robocorp'Window Test1 class:Class classx:Classx Test2",
                [
                    ("name", "Robocorp'Window Test1", 0),
                    ("class", "Class", 0),
                    ("name", "classx:Classx Test2", 0),
                ],
            ),
            ("'Robocorp Window'", [("name", "'Robocorp Window'", 0)]),
            (
                "name:'Robocorp Window'",
                [("name", "'Robocorp", 0), ("name", "Window'", 0)],
            ),  # single quotes don't work for enclosing, use double
            ('Robocorp" Window', [("name", 'Robocorp" Window', 0)]),
            (
                'name:Robocorp" Window class:"My Class"',
                [("name", 'Robocorp" Window class:', 0), ("name", "My Class", 0)],
            ),  # enclosing quotes have to be closed properly
            (
                'name:"Robocorp" Window" class:"My Class"',
                [("name", 'Robocorp" Window', 0), ("class", "My Class", 0)],
            ),  # lucky capture
            (
                'name:"Robocorp " Window" class:"My Class"',
                [("name", "Robocorp", 0), ("name", 'Window" class:" My Class', 0)],
            ),  # can't capture same quote in enclosing ones
            ("", []),
            (
                "Robo and Corp or Window desktop",
                [("desktop", "desktop", 0), ("name", "Robo Corp Window", 0)],
            ),
            (
                "id:123-456 depth:10 subname:Robo offset:100 executable:my.exe",
                [
                    ("id", "123-456", 0),
                    ("depth", 10, 0),
                    ("subname", "Robo", 0),
                    ("offset", "100", 0),
                    ("executable", "my.exe", 0),
                ],
            ),
            (
                'type:Group and name:"Number pad" > type:Button and index:4',
                [
                    ("control", "GroupControl", 0),
                    ("name", "Number pad", 0),
                    ("control", "ButtonControl", 1),
                    ("index", 4, 1),
                ],
            ),
            (
                "Calculator > path:2|3|2|8|2",
                [("name", "Calculator", 0), ("path", [2, 3, 2, 8, 2], 1)],
            ),
        ],
    )
    def test_match_object(self, locator, locators):
        from robocorp.windows._match_object import MatchObject

        match_object = MatchObject.parse_locator(locator)
        assert match_object.locators == locators
