from argparse import (
    ArgumentParser as _ArgumentParser,
    Namespace as _Namespace,
    HelpFormatter as _HelpFormatter
)
from typing import (
    Callable as _Callable
)

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

    def __init__(self, fn: _Callable[[_Namespace], int],
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

    def __call__(self, args=None, namespace=None) -> int:
        _args = self._parser.parse_args(args, namespace)
        sub: _CommandWrapper = self.__getSubCommand(_args)
        if sub:
            return sub.__runImpl(_args)
        else:
            return self.__runImpl(_args)

    def __runImpl(self, args: _Namespace) -> int:
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
    return _ArgumentWrapper(*name_or_flags,
                            action=action,
                            nargs=nargs,
                            const=const,
                            default=default,
                            type=type,
                            choices=choices,
                            required=required,
                            help=help,
                            metavar=metavar,
                            dest=dest)


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

    assert isinstance(name, str), \
        f"invalid name for command: {name}"
    assert isinstance(parent, _CommandWrapper) or parent == None, \
        f"invalid parent for command |{name}|."
    assert all(isinstance(x, _ArgumentWrapper) for x in args), \
        f"invalid arguments for command |{name}|."
    assert all(isinstance(x, _CommandWrapper) for x in parents), \
        f"invalid parents for command |{name}|."

    parents = [x._getParser() for x in parents]

    def decorate(func):
        nonlocal name
        nonlocal args
        nonlocal parent
        nonlocal help
        nonlocal need_sub
        nonlocal skippable
        nonlocal usage
        nonlocal description
        nonlocal epilog
        nonlocal formatter_class
        nonlocal prefix_chars
        nonlocal fromfile_prefix_chars
        nonlocal argument_default
        nonlocal conflict_handler
        nonlocal add_help
        nonlocal allow_abbrev
        nonlocal exit_on_error

        cmd_wrapper: _CommandWrapper = None

        if parent == None:
            # root command condition.
            raw_parser = _ArgumentParser(prog=name,
                                         usage=usage,
                                         description=description,
                                         epilog=epilog,
                                         parents=parents,
                                         formatter_class=formatter_class,
                                         prefix_chars=prefix_chars,
                                         fromfile_prefix_chars=fromfile_prefix_chars,
                                         argument_default=argument_default,
                                         conflict_handler=conflict_handler,
                                         add_help=add_help,
                                         allow_abbrev=allow_abbrev,
                                         exit_on_error=exit_on_error)

            cmd_wrapper = _CommandWrapper(func, raw_parser,
                                          parent=None,
                                          required_subcmd=need_sub,
                                          skip_if_has_subcmd=skippable)
        else:
            # sub command condition.
            assert isinstance(parent, _CommandWrapper), \
                f"invalid parent for command |{name}|."
            sub_paresr = parent._addSubParser(name,
                                              prog=name,
                                              usage=usage,
                                              help=help,
                                              description=description,
                                              epilog=epilog,
                                              parents=parents,
                                              formatter_class=formatter_class,
                                              prefix_chars=prefix_chars,
                                              fromfile_prefix_chars=fromfile_prefix_chars,
                                              argument_default=argument_default,
                                              conflict_handler=conflict_handler,
                                              add_help=add_help,
                                              allow_abbrev=allow_abbrev,
                                              exit_on_error=exit_on_error)

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

    return decorate
