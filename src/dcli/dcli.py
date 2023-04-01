from argparse import (
    ArgumentParser as _ArgumentParser,
    Namespace as _Namespace,
    HelpFormatter as _HelpFormatter
)
from typing import (
    Callable as _Callable, Any
)

MAJOR_VERSION = 0
MINOR_VERSION = 1
PATCH_VERSION = 3

VERSION = f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}"

# public symbols
__all__ = ["arg", "command"]
__version__ = VERSION


_SUBCMD_SPECIFIER = "__sub_cmd_wrapper__"


class _ArgumentWrapper:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs


class _CommandWrapper:
    """
    Class _CommandWrapper is an |argparse| wrapper for decorated function.

    Usage:
    @dcli.command(...) 
    def Command(args: argparse.Namespace):
      ...

    Then calling |Command()| directly will invoke argpaser.parse_args() and pass return value into the origin function |Command(args)|.
    """

    def __init__(self, fn: _Callable[[_Namespace], Any],
                 parser: _ArgumentParser,
                 *,
                 parent=None,
                 required_subcmd: bool = True,
                 skip_if_has_subcmd: bool = True) -> None:
        self._fn = fn
        self._parser = parser
        self._subparsers = None
        self._parent_cmd = parent
        self._required_sub = required_subcmd
        self._skip_if_has_subcmd = skip_if_has_subcmd

    def __getSubCommand(self, args: _Namespace):
        if not hasattr(args, _SUBCMD_SPECIFIER) or not isinstance(getattr(args, _SUBCMD_SPECIFIER), _CommandWrapper):
            return None
        else:
            return getattr(args, _SUBCMD_SPECIFIER)

    def __call__(self, args=None, namespace=None) -> Any:
        _args = self._parser.parse_args(args, namespace)
        sub: _CommandWrapper = self.__getSubCommand(_args)
        if sub:
            return sub.__runImpl(_args)
        else:
            return self.__runImpl(_args)

    def __runImpl(self, args: _Namespace) -> Any:
        if self._parent_cmd and isinstance(self._parent_cmd, _CommandWrapper):
            return self._parent_cmd.__runImpl(args)
        sub = self.__getSubCommand(args)
        if not sub or not self._skip_if_has_subcmd:
            return self._fn(args)

    def _addSubParser(self, name: str, **kwargs) -> _ArgumentParser:
        if self._subparsers == None:
            self._subparsers = self._getParser().add_subparsers()
        self._subparsers.required = self._required_sub
        return self._subparsers.add_parser(name, **kwargs)

    def _getParser(self) -> _ArgumentParser:
        return self._parser

    def _addArgument(self, arg: _ArgumentWrapper):
        self._getParser().add_argument(*arg.args, **arg.kwargs)


def arg(*name_or_flags: str,
        action=None,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=None,
        help=None,
        metavar=None,
        dest=None):
    """Wrapper for add_argument.

    Keyword Arguments:
        - name_or_flags -- Either a name or a list of option strings, e.g. foo or -f, --foo
        - action -- Specify how an argument should be handled
        - nargs -- Number of times the argument can be used
        - const -- Store a constant value
        - default -- Default value used when an argument is not provided
        - type -- Automatically convert an argument to the given type
        - choices -- Limit values to a specific set of choices
        - required -- Indicate whether an argument is required or optional
        - help -- Help message for an argument
        - metavar -- Alternate display name for the argument as shown in help
        - dest -- Specify the attribute name used in the result namespace

    See https://docs.python.org/3/library/argparse.html#the-add-argument-method for more information.
    """

    kwarg = {}
    if action != None:
        kwarg["action"] = action
    if nargs != None:
        kwarg["nargs"] = nargs
    if const != None:
        kwarg["const"] = const
    if default != None:
        kwarg["default"] = default
    if type != None:
        kwarg["type"] = type
    if choices != None:
        kwarg["choices"] = choices
    if required != None:
        kwarg["required"] = required
    if help != None:
        kwarg["help"] = help
    if metavar != None:
        kwarg["metavar"] = metavar
    if dest != None:
        kwarg["dest"] = dest

    return _ArgumentWrapper(*name_or_flags, **kwarg)


def command(name: str,
            *args: _ArgumentWrapper,
            parent=None,
            parents=[],
            help="",
            need_sub=True,
            skippable=True,
            usage=None,
            description=None,
            epilog=None,
            formatter_class=_HelpFormatter,
            prefix_chars='-',
            fromfile_prefix_chars=None,
            argument_default=None,
            conflict_handler='error',
            add_help=True,
            allow_abbrev=True,
            exit_on_error=True):
    """Decorator for parsing command line strings and running if necessary.

    Keyword Arguments:
        - name -- The name of the command
        - args -- The arguments for this command
        - parent -- The parent command, this one will be a subcommand of parent
        - parents -- Parsers whose arguments should be copied into this one
        - help -- The short help message for command
        - need_sub -- Specifier whether this command requires subcommand
        - skippable -- Specifier whether skip this one if subcommand triggered
        - usage -- A usage message (default: auto-generated from arguments)
        - description -- A description of what the program does
        - epilog -- Text following the argument descriptions
        - formatter_class -- HelpFormatter class for printing help messages
        - prefix_chars -- Characters that prefix optional arguments
        - fromfile_prefix_chars -- Characters that prefix files containing additional arguments
        - argument_default -- The default value for all arguments
        - conflict_handler -- String indicating how to handle conflicts
        - add_help -- Add a -h/-help option
        - allow_abbrev -- Allow long options to be abbreviated unambiguously
        - exit_on_error -- Determines whether or not ArgumentParser exits with error info when an error occurs

    See https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser for more information.
    """

    assert isinstance(name, str), \
        f"invalid name for command: {name}"
    assert isinstance(parent, _CommandWrapper) or parent == None, \
        f"invalid parent for command |{name}|."
    assert all(isinstance(x, _ArgumentWrapper) for x in args), \
        f"invalid arguments for command |{name}|."
    assert all(isinstance(x, _CommandWrapper) for x in parents), \
        f"invalid parents for command |{name}|."

    parents = [x._getParser() for x in parents]

    parser_kwargs = {}
    parser_kwargs["prog"] = name
    parser_kwargs["usage"] = usage
    parser_kwargs["description"] = description
    parser_kwargs["epilog"] = epilog
    parser_kwargs["formatter_class"] = formatter_class
    parser_kwargs["prefix_chars"] = prefix_chars
    parser_kwargs["fromfile_prefix_chars"] = fromfile_prefix_chars
    parser_kwargs["argument_default"] = argument_default
    parser_kwargs["conflict_handler"] = conflict_handler
    parser_kwargs["add_help"] = add_help
    parser_kwargs["allow_abbrev"] = allow_abbrev
    parser_kwargs["exit_on_error"] = exit_on_error

    def deorator(func):
        nonlocal name
        nonlocal args
        nonlocal parent
        nonlocal help
        nonlocal need_sub
        nonlocal skippable
        nonlocal parser_kwargs

        cmd_wrapper: _CommandWrapper = None

        if parent == None:
            # root command condition.
            raw_parser = _ArgumentParser(**parser_kwargs)

            cmd_wrapper = _CommandWrapper(func, raw_parser,
                                          parent=None,
                                          required_subcmd=need_sub,
                                          skip_if_has_subcmd=skippable)
        else:
            # sub command condition.
            assert isinstance(parent, _CommandWrapper), \
                f"invalid parent for command |{name}|."
            sub_paresr = parent._addSubParser(name, help=help, **parser_kwargs)

            cmd_wrapper = _CommandWrapper(func, sub_paresr,
                                          parent=parent,
                                          required_subcmd=need_sub,
                                          skip_if_has_subcmd=skippable)

            sub_paresr.set_defaults(**{_SUBCMD_SPECIFIER: cmd_wrapper})

        # add arguments
        for arg in args:
            cmd_wrapper._addArgument(arg)

        assert cmd_wrapper != None, "something went wrong!"
        return cmd_wrapper

    return deorator
