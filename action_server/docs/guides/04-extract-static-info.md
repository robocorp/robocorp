## Extracting static information from an Action Package

The basic structure of an Action Package contains a `package.yaml` at the
root and then it can contain multiple actions (defined as `@action`) in
the code.

To have the full information of everything, the action server provides
the `openapi.json`, which can be gotten by starting the action server
with the required action packages and then make a request for the `/openapi.json`
url (for instance `http://localhost:8080/openapi.json`).

Unfortunately this can be a very expensive process as it requires the full
environment in which the action can be actually imported.

Given that, the Action Server provides a faster way to extract basic information
from an Action Package.

### Command line

To extract basic information from an Action Package, it's possible to use:

`action-server package-information <action package root dir>`

The output of this command will give as an output a json sent to the `stdout`
with the contents below:

```
{
  // Name of the package
  "action-package": {
    "name": "package-name",
    "yaml-file": "<path to package.yaml, conda.yaml or action-server.yaml>",
    "description": ""
  },
  // The actions found and where they're defined
  "actions": [
    {
      "name": "action 1",
      "description": "Description of the action",
      "arguments": [
        // Note: the type of the argument cannot be always detected (so, if some argument actually
        // maps to a complex object or the user uses some alias for str, int, etc it won't be available)
        { "name": "argument name", "description": "argument description", "type": "string" }
      ],
      "file": "path to file",
      "range": {
        "start": { "line": 0, "character": 0 },
        "end": { "line": 0, "character": 22 }
      }
    }
  ],
  // Errors or information on the action package
  // (for instance, if the package.yaml is not valid
  // or if the docstring for the action is not valid, etc)
  "lint": [
    {
      "file": "path to file",
      "diagnostics": [
        {
          // range is optional, but if available point to
          // the location in the  file to where the error
          // is linked
          "range": {
            "start": { "line": 0, "character": 0 },
            "end": { "line": 0, "character": 22 }
          },
          // Severities:
          // Error = 1
          // Warning = 2
          // Information = 3
          // Hint = 4
          "severity": 1,
          "source": "robocorp.actions",
          "message": "Error message"
        }
      ]
    }
  ]
}
```

### Notes

Note that the user is required to use `@action` as the actual decorator. If
an alias is used the action will not be found. As such, the action server itself
will do that validation and should refuse to import actions which are not
properly marked as such and should let the user know about it.

This makes the python code a bit less flexible in how the action can be defined
but it helps all tools which need to statically analyze the code (which was decided
to be a worthy tradeoff).