# robocorp-actions

`robocorp-actions` is a Python framework designed to simplify the development 
of Python actions (AI or otherwise) to be run in the `Robocorp Action Server`.


## Getting started

Replace the code in your `__main__` with a method that has the name of your action
and decorate it with the `@action` decorator, like this:

i.e.:


```python
from robocorp.actions import action

@action
def sum_numbers(a: float, b: float) -> float:
    ...
```

Note: it's expected that the action arguments and action return are properly
typed (if a type is not specified, `str` is considered for it).

Note: only `int`, `float`, `str` and `bool` types are currently supported.

The entry points for the values should be passed by the `Robocorp Action Server`,
but it's also possible to provide them in the command line by passing them in
named arguments after a `--`.

Example:


```sh
python -m robocorp.actions -- --a=2 --b=3
```

When used in the `Robocorp Action Server`, an Open API spec (`openapi.json`) 
is provided to be comformat to these parameters (the `Robocorp Action Server` 
manages passing the arguments accordingly and returning the result afterwards).

## API Reference

Information on specific functions or classes: [robocorp.actions](https://github.com/robocorp/robocorp/blob/master/actions/docs/api/README.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/actions/docs/CHANGELOG.md).
