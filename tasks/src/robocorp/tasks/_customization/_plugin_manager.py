# Original work Copyright 2018 Brainwy Software Ltda (Dual Licensed: LGPL / Apache 2.0)
# From https://github.com/fabioz/pyvmmonitor-core
# See ThirdPartyNotices.txt in the project root for license information.
# All modifications Copyright (c) Robocorp Technologies Inc.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http: // www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Defines a PluginManager (which doesn't really have plugins, only a registry of extension points
and implementations for such extension points).

To use, create the extension points you want (any class starting with 'EP') and register
implementations for those.

I.e.:
pm = PluginManager()
pm.register(EPFoo, FooImpl, keep_instance=True)
pm.register(EPBar, BarImpl, keep_instance=False)

Then, later, to use it, it's possible to ask for instances through the PluginManager API:

foo_instances = pm.get_implementations(EPFoo) # Each time this is called, new
                                              # foo_instances will be created
                                              
bar_instance = pm.get_instance(EPBar) # Each time this is called, the same bar_instance is returned.

Alternatively, it's possible to use a decorator to use a dependency injection pattern -- i.e.:
don't call me, I'll call you ;)

@inject(foo_instance=EPFoo, bar_instances=[EPBar])
def m1(foo_instance, bar_instances, pm):
    for bar in bar_instances:
        ...
    foo_instance.foo
    
"""
import functools
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Type, TypeVar, Union


def execfile(file, glob=None, loc=None):
    import tokenize

    with tokenize.open(file) as stream:
        contents = stream.read()

    exec(compile(contents + "\n", file, "exec"), glob, loc)


class NotInstanceError(RuntimeError):
    pass


class NotRegisteredError(RuntimeError):
    pass


class InstanceAlreadyRegisteredError(RuntimeError):
    pass


T = TypeVar("T")


class PluginManager(object):
    """
    This is a manager of plugins (which we refer to extension points and implementations).
    Mostly, we have a number of EPs (Extension Points) and implementations may be registered
    for those extension points.
    The PluginManager is able to provide implementations (through #get_implementations) which are
    not kept on being tracked and a special concept which keeps an instance alive for an extension
    (through #get_instance).
    """

    def __init__(self) -> None:
        self._ep_to_impls: Dict[Type, list] = {}
        self._ep_to_instance_impls: Dict[Tuple[Type, Optional[str]], list] = {}
        self._ep_to_context_to_instance: Dict[Type, dict] = {}
        self._name_to_ep: Dict[str, Type] = {}
        self.exited = False

    def load_plugins_from(self, directory: Path) -> int:
        found_files_with_plugins = 0
        filepath: Path
        for filepath in directory.iterdir():
            if filepath.is_file() and filepath.name.endswith(".py"):
                namespace: dict = {"__file__": str(filepath)}
                execfile(str(filepath), glob=namespace, loc=namespace)
                register_plugins = namespace.get("register_plugins")
                if register_plugins is not None:
                    found_files_with_plugins += 1
                    register_plugins(self)
        return found_files_with_plugins

    # This should be:
    # def get_implementations(self, ep: Type[T]) -> List[T]:
    # But isn't due to: https://github.com/python/mypy/issues/5374
    def get_implementations(self, ep: Union[Type, str]) -> list:
        assert not self.exited
        if isinstance(ep, str):
            ep = self._name_to_ep[ep]

        impls = self._ep_to_impls.get(ep, [])
        ret = []
        for class_, kwargs in impls:
            instance = class_(**kwargs)
            ret.append(instance)

        return ret

    def register(
        self,
        ep: Type,
        impl,
        kwargs: Optional[dict] = None,
        context: Optional[str] = None,
        keep_instance: bool = False,
    ):
        """
        :param ep:
        :param str impl:
            This is the full path to the class implementation.
        :param kwargs:
        :param context:
            If keep_instance is True, it's possible to register it for a given
            context.
        :param keep_instance:
            If True, it'll be only available through pm.get_instance and the
            instance will be kept for further calls.
            If False, it'll only be available through get_implementations.
        """
        if kwargs is None:
            kwargs = {}
        assert not self.exited
        if isinstance(ep, str):
            raise ValueError("Expected the actual EP class to be passed.")
        self._name_to_ep[ep.__name__] = ep

        if keep_instance:
            ep_to_instance_impls = self._ep_to_instance_impls
            impls = ep_to_instance_impls.get((ep, context))
            if impls is None:
                impls = ep_to_instance_impls[(ep, context)] = []
            else:
                raise InstanceAlreadyRegisteredError(
                    "Unable to override when instance is kept and an implementation "
                    "is already registered."
                )
        else:
            ep_to_impl = self._ep_to_impls
            impls = ep_to_impl.get(ep)
            if impls is None:
                impls = ep_to_impl[ep] = []

        impls.append((impl, kwargs))

    def unregister(
        self, ep: Type, context: Optional[str] = None, keep_instance: bool = False
    ):
        self._name_to_ep.pop(ep.__name__, None)
        if keep_instance:
            ep_to_instance_impls = self._ep_to_instance_impls
            ep_to_instance_impls.pop((ep, context), None)
        else:
            ep_to_impl = self._ep_to_impls
            ep_to_impl.pop(ep, None)

    def set_instance(self, ep: Type, instance, context=None) -> None:
        if isinstance(ep, str):
            raise ValueError("Expected the actual EP class to be passed.")
        self._name_to_ep[ep.__name__] = ep

        instances = self._ep_to_context_to_instance.get(ep)
        if instances is None:
            instances = self._ep_to_context_to_instance[ep] = {}
        instances[context] = instance

    def iter_existing_instances(self, ep: Union[Type, str]):
        if isinstance(ep, str):
            ep = self._name_to_ep[ep]

        return self._ep_to_context_to_instance[ep].values()

    def has_instance(self, ep: Union[Type, str], context=None):
        if isinstance(ep, str):
            ep_cls = self._name_to_ep.get(ep)
            if ep_cls is None:
                return False

        try:
            self.get_instance(ep, context)
            return True
        except NotRegisteredError:
            return False

    # This should be:
    # def get_instance(self, ep: Type[T], context=None) -> T:
    # But isn't due to: https://github.com/python/mypy/issues/5374
    def get_instance(self, ep: Union[Type, str], context: Optional[str] = None) -> Any:
        """
        Creates an instance in this plugin manager: Meaning that whenever a new EP is asked in
        the same context it'll receive the same instance created previously (and it'll be
        kept alive in the plugin manager).
        """
        if self.exited:
            raise AssertionError("PluginManager already exited")

        if isinstance(ep, str):
            ep = self._name_to_ep[ep]
        try:
            return self._ep_to_context_to_instance[ep][context]
        except KeyError:
            try:
                impls = self._ep_to_instance_impls[(ep, context)]
            except KeyError:
                found = False
                if context is not None:
                    found = True
                    try:
                        impls = self._ep_to_instance_impls[(ep, None)]
                    except KeyError:
                        found = False
                if not found:
                    if ep in self._ep_to_impls:
                        # Registered but not a kept instance.
                        raise NotInstanceError()
                    else:
                        # Not registered at all.
                        raise NotRegisteredError()
            assert len(impls) == 1
            class_, kwargs = impls[0]

            instances = self._ep_to_context_to_instance.get(ep)
            if instances is None:
                instances = self._ep_to_context_to_instance[ep] = {}

            ret = instances[context] = class_(**kwargs)
            return ret

    __getitem__ = get_instance

    def exit(self):
        self.exited = True
        self._ep_to_context_to_instance.clear()
        self._ep_to_impls.clear()


def inject(**inject_kwargs):
    def decorator(func):
        @functools.wraps(func)
        def inject_dec(*args, **kwargs):
            pm = kwargs.get("pm")
            if pm is None:
                raise AssertionError(
                    "pm argument with PluginManager not passed (required for @inject)."
                )

            for key, val in inject_kwargs.items():
                if key not in kwargs:
                    if val.__class__ is list:
                        kwargs[key] = pm.get_implementations(val[0])
                    else:
                        kwargs[key] = pm.get_instance(val)
            return func(*args, **kwargs)

        return inject_dec

    return decorator
