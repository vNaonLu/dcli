# dcli

[![cicd](https://github.com/vNaonLu/dcli/actions/workflows/cicd.yml/badge.svg)](https://github.com/vNaonLu/dcli/actions)

**dcli** is a nested functional-oriented cli (command line interface) python module. **dcli** does not require any other third-party module, it just wraps and encapsolutes [argparse](https://docs.python.org/3/library/argparse.html) in a decorator, i.e. `@dcli.command()`.

## Requirements

While **dcli** does not require any third-party, it requires run in Python with specific versions.

- above Python 3.9

## Getting Started

To create our own command, just type following code:

```python
@dcli.command(
    "MyCommand",
    dcli.arg(...),
    dcli.arg(...),
    ...
)
def MyCommand(namespace):
  ...

...
# call the command function directly to parse the arguments from program.
MyCommand()
```

`namespace` which is of type [argparse.Namespace](https://docs.python.org/3/library/argparse.html#the-namespace-object) will be passed from [ArgumentParser.parse_args()](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args). We can directly call `MyCommand()` without any parameters to parse the program arguments and then the original function `MyCommand(namespace)` will be invoked once `parse_args()` done. For advanced usage, it is possible to pass parameter `args` into `MyCommand()` to parse custom arguments, e.g.

```python
MyCommand('--baz')
MyCommand(['-x', 'X'])
MyCommand(['--foo', 'bar'])
```

**dcli** also support subcommand:

``` python
@dcli.command(
    "COMMAND_NAME",
    dcli.arg(...),
    dcli.arg(...),
    ...,
    parent=MyCommand
)
def SubCommand(namespace):
  ...

MyCommand()
```

The above code will make `SubCommand` be a subcommand in `MyCommand` and named in `COMMAND_NAME`. By calling `MyCommand(["COMMAND_NAME"])`, we can easily trigger `SubCommand(namespace)` and do what we want.
