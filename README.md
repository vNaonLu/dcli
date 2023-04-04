# dcli

[![cicd](https://github.com/vNaonLu/dcli/actions/workflows/cicd.yml/badge.svg)](https://github.com/vNaonLu/dcli/actions)

**dcli** is a nested functional-oriented cli (command line interface) python module. **dcli** does not require any other third-party module, it just wraps and encapsolutes [argparse](https://docs.python.org/3/library/argparse.html) in a decorator, i.e. `@dcli.command()`.

## Getting Started

Before installing, see [Requirements](#requirements) to check the dependencies.

See [Installation](#installation) to install **dcli** to your local environment and [Tutorial](#tutorial) for more information about how to use.


## Requirements

While **dcli** does not require any third-party, it requires run in Python with specific versions.

- above Python 3.9

## Installation

Only one step to install **dcli**:

```sh
$ python3 -m pip install decorator-cli

# pip list to check installation
$ python3 -m pip list

Package       Version
------------- ---------
decorator-cli <version>
```

## Tutorial

To create our own command `MyCommand` via **dcli**

``` python
# my-command.py
import dcli

@dcli.command(
  "MyCommand",
  dcli.arg("-f", "--foo", dest="bar", default=False, action="store_true",
           help="I am 'foo' identifier!"),
  description="This is my command!"
)
def MyCommand(ns):
  print("Hello World")
  print("--foo", getattr(ns, "bar"))
```

The only paremeter `ns` in `MyCommand` is type of `argparse.Namespace`, and will be passed from `parse_args()`. See [Namespace](https://docs.python.org/3/library/argparse.html#argparse.Namespace) for more information.

`@dcli.command` encapsolutes the class `argparse.ArgumentParser`, and all parameters from `argparse.ArgumentParser` are available for `@dcli.command`, just note that the parameters should be passed as `kwargs`.
 `dcli.arg()` just wraps the parameters from `argparse.ArgumentParser.add_argument()`, please see [add_argument()](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument) for more information about how to add argument. In addition, it is possible to add multiple `dcli.arg` in a single command `@dcli.command`. 

``` python
@dcli.command(
  "SomeCommand"
  dcli.arg("--foo", ...),
  dcli.arg("--bar", ...),
  dcli.arg("--baz", ...),
  ...
)
def SomeCommand(ns):
  ...
```

Once we defined our command `MyCommand`, we can easily trigger our command by

``` python
# my-command.py
MyCommand()
```

``` sh
# in shell
# auto-generated help message.
$ python3 path/to/my-command.py -h
usage: MyCommand [-h] [-f]

This is my command!

options:
  -h, --help  show this help message and exit
  -f, --foo   I am 'foo' identifier!

# pass some argument.
$ python3 path/to/my-command.py -f
Hello World
--foo True
```

`MyCommand()` is a decorated function which combine `parse_args()` and pass the result into the user-defined function. For advanced usage, if we need to do some test for `MyCommand`, it is possible to pass an argument to it instead of a default value as `sys.argv`.

``` python
MyCommand("--foo")
MyCommand([])
MyCommand(["-x", "X"])
MyCommand(["-foo", "bar"])
```

**dcli** also provides subcommand creation. There are two ways to define subcommand.

- By decorated function

    ``` python
    # my-command.py
    @dcli.command("sub1", parent=MyCommand,
                  help="I am sub command #1.")
    def SubCommand1(ns):
      print("I am sub command #1.")
    ```

- By add manually

    ``` python
    # my-command.py
    @dcli.command("sub2",
                  help="I am sub command #2.")
    def SubCommand2(ns):
      print("I am sub command #2.")
    ...
    MyCommand.addSubCommand(SubCommand2)
    ```

And trigger `MyCommand` as usual.

``` python
# my-command.py
MyCommand()
```

``` sh
# in shell
# auto-generated help message.
$ python3 path/to/my-command.py -h
usage: MyCommand [-h] {sub1,sub2} ...

positional arguments:
  {sub1,sub2}
    sub1       I am sub command #1.
    sub2       I am sub command #2.

options:
  -h, --help   show this help message and exit

# trigger subcommand
$ python3 path/to/my-command.py sub1
I am sub command #1.
$ python3 path/to/my-command.py sub2
I am sub command #2.
```

It is possible to invoke `SubCommand1()` or `SubCommand2()` directly if you want to test them.