# Original work Copyright (C) 2013 Chase Sterling (MIT license)
# https://github.com/gazpachoking/jsonref/blob/master/jsonref/__init__.py
#
# Changes:
# No collecting of external uris.
# No lazy-loading (references are always replaced).
# Early error when a cyclic reference is found.
#
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
from collections.abc import Mapping, MutableMapping, Sequence
from urllib import parse as urlparse
from urllib.parse import unquote


class CallbackProxy(object):
    """
    Proxy for a callback result. Callback is called on each use.

    """

    def __init__(self, callback):
        self.callback = callback

    @property
    def __subject__(self):
        return self.callback()


class LazyProxy(CallbackProxy):
    """
    Proxy for a callback result, that is cached on first use.

    """

    @property
    def __subject__(self):
        try:
            return self.cache
        except AttributeError:
            pass

        self.cache = super(LazyProxy, self).__subject__
        return self.cache

    @__subject__.setter
    def __subject__(self, value):
        self.cache = value


class JsonRefError(Exception):
    def __init__(self, message, reference, uri="", base_uri="", path=(), cause=None):
        self.message = message
        self.reference = reference
        self.uri = uri
        self.base_uri = base_uri
        self.path = path
        self.cause = self.__cause__ = cause

    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.message)

    def __str__(self):
        return str(self.message)


class JsonRef(LazyProxy):
    """
    A lazy loading proxy to the dereferenced data pointed to by a JSON
    Reference object.

    """

    __notproxied__ = ("__reference__",)

    @classmethod
    def replace_refs(cls, obj, base_uri="", jsonschema=False, load_on_repr=True):
        """
        .. deprecated:: 0.4
            Use :func:`replace_refs` instead.

        Returns a deep copy of `obj` with all contained JSON reference objects
        replaced with :class:`JsonRef` instances.

        :param obj: If this is a JSON reference object, a :class:`JsonRef`
            instance will be created. If `obj` is not a JSON reference object,
            a deep copy of it will be created with all contained JSON
            reference objects replaced by :class:`JsonRef` instances
        :param base_uri: URI to resolve relative references against
        :param jsonschema: Flag to turn on `JSON Schema mode
            <http://json-schema.org/latest/json-schema-core.html#anchor25>`_.
            'id' keyword changes the `base_uri` for references contained within
            the object
        :param load_on_repr: If set to ``False``, :func:`repr` call on a
            :class:`JsonRef` object will not cause the reference to be loaded
            if it hasn't already. (defaults to ``True``)

        """
        return replace_refs(
            obj,
            base_uri=base_uri,
            jsonschema=jsonschema,
            load_on_repr=load_on_repr,
        )

    _resolving_ref = 0

    def __init__(
        self,
        refobj,
        base_uri="",
        jsonschema=False,
        load_on_repr=True,
        merge_props=False,
        _path=(),
        _store=None,
    ):
        if not isinstance(refobj.get("$ref"), str):
            raise ValueError("Not a valid json reference object: %s" % refobj)
        self.__reference__ = refobj
        self.base_uri = base_uri
        self.jsonschema = jsonschema
        self.load_on_repr = load_on_repr
        self.merge_props = merge_props
        self.path = _path
        self.store = _store  # Use the same object to be shared with children
        if self.store is None:
            self.store = URIDict()

    @property
    def _ref_kwargs(self):
        return dict(
            base_uri=self.base_uri,
            jsonschema=self.jsonschema,
            load_on_repr=self.load_on_repr,
            merge_props=self.merge_props,
            path=self.path,
            store=self.store,
        )

    @property
    def full_uri(self):
        return urlparse.urljoin(self.base_uri, self.__reference__["$ref"])

    def callback(self):
        if self._resolving_ref:
            raise self._error(
                "It seems that there is a cyclic reference in the schema."
            )
        try:
            self._resolving_ref += 1
            uri, fragment = urlparse.urldefrag(self.full_uri)

            # If we already looked this up, return a reference to the same object
            if uri not in self.store:
                base_doc = self
            else:
                base_doc = self.store[uri]
            result = self.resolve_pointer(base_doc, fragment)
            if result is self:
                raise self._error("Reference refers directly to itself.")
            if hasattr(result, "__subject__"):
                result = result.__subject__
            if (
                self.merge_props
                and isinstance(result, Mapping)
                and len(self.__reference__) > 1
            ):
                result = {
                    **result,
                    **{k: v for k, v in self.__reference__.items() if k != "$ref"},
                }
        finally:
            self._resolving_ref -= 1
        return result

    def resolve_pointer(self, document, pointer):
        """
        Resolve a json pointer ``pointer`` within the referenced ``document``.

        :argument document: the referent document
        :argument str pointer: a json pointer URI fragment to resolve within it

        """
        parts = unquote(pointer.lstrip("/")).split("/") if pointer else []

        for part in parts:
            part = part.replace("~1", "/").replace("~0", "~")

            if isinstance(document, Sequence):
                # Try to turn an array index to an int
                try:
                    part = int(part)
                except ValueError:
                    pass
            # If a reference points inside itself, it must mean inside reference object, not the referent data
            if document is self:
                document = self.__reference__
            try:
                document = document[part]
            except (TypeError, LookupError) as e:
                raise self._error(
                    "Unresolvable JSON pointer: %r" % pointer, cause=e
                ) from e
        return document

    def _error(self, message, cause=None):
        message = "Error while resolving `{}`: {}".format(self.full_uri, message)
        return JsonRefError(
            message,
            self.__reference__,
            uri=self.full_uri,
            base_uri=self.base_uri,
            path=self.path,
            cause=cause,
        )

    def __repr__(self):
        if hasattr(self, "cache") or self.load_on_repr:
            return repr(self.__subject__)
        return "JsonRef(%r)" % self.__reference__


class URIDict(MutableMapping):
    """
    Dictionary which uses normalized URIs as keys.
    """

    def normalize(self, uri):
        return urlparse.urlsplit(uri).geturl()

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.store.update(*args, **kwargs)

    def __getitem__(self, uri):
        return self.store[self.normalize(uri)]

    def __setitem__(self, uri, value):
        self.store[self.normalize(uri)] = value

    def __delitem__(self, uri):
        del self.store[self.normalize(uri)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        return repr(self.store)


def _walk_refs(obj, func, replace=False, _processed=None):
    # Keep track of already processed items to prevent recursion
    _processed = _processed or {}
    oid = id(obj)
    if oid in _processed:
        return _processed[oid]
    if type(obj) is JsonRef:
        r = func(obj)
        obj = r if replace else obj
    _processed[oid] = obj
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            r = _walk_refs(v, func, replace=replace, _processed=_processed)
            if replace:
                obj[k] = r
    elif isinstance(obj, Sequence) and not isinstance(obj, str):
        for i, v in enumerate(obj):
            r = _walk_refs(v, func, replace=replace, _processed=_processed)
            if replace:
                obj[i] = r
    return obj


def replace_refs(
    obj,
    base_uri="",
    jsonschema=False,
    load_on_repr=True,
    merge_props=False,
):
    """
    Returns a deep copy of `obj` with all contained JSON reference objects
    replaced with :class:`JsonRef` instances.

    :param obj: If this is a JSON reference object, a :class:`JsonRef`
        instance will be created. If `obj` is not a JSON reference object,
        a deep copy of it will be created with all contained JSON
        reference objects replaced by :class:`JsonRef` instances
    :param base_uri: URI to resolve relative references against
    :param jsonschema: Flag to turn on `JSON Schema mode
        <http://json-schema.org/latest/json-schema-core.html#anchor25>`_.
        'id' or '$id' keyword changes the `base_uri` for references contained
        within the object
    :param load_on_repr: If set to ``False``, :func:`repr` call on a
        :class:`JsonRef` object will not cause the reference to be loaded
        if it hasn't already. (defaults to ``True``)
    :param merge_props: When ``True``, JSON reference objects that
        have extra keys other than '$ref' in them will be merged into the
        document resolved by the reference (if it is a dictionary.) NOTE: This
        is not part of the JSON Reference spec, and may not behave the same as
        other libraries.
    """
    result = _replace_refs(
        obj,
        base_uri=base_uri,
        jsonschema=jsonschema,
        load_on_repr=load_on_repr,
        merge_props=merge_props,
        store=URIDict(),
        path=(),
        recursing=False,
    )
    _walk_refs(result, lambda r: r.__subject__, replace=True)
    return result


def _replace_refs(
    obj,
    *,
    base_uri,
    jsonschema,
    load_on_repr,
    merge_props,
    store,
    path,
    recursing,
):
    base_uri, frag = urlparse.urldefrag(base_uri)
    store_uri = None  # If this does not get set, we won't store the result
    if not frag and not recursing:
        store_uri = base_uri
    if jsonschema and isinstance(obj, Mapping):
        # id changed to $id in later jsonschema versions
        id_ = obj.get("$id") or obj.get("id")
        if isinstance(id_, str):
            base_uri = urlparse.urljoin(base_uri, id_)
            store_uri = base_uri

    # First recursively iterate through our object, replacing children with JsonRefs
    if isinstance(obj, Mapping):
        obj = {
            k: _replace_refs(
                v,
                base_uri=base_uri,
                jsonschema=jsonschema,
                load_on_repr=load_on_repr,
                merge_props=merge_props,
                store=store,
                path=path + (k,),
                recursing=True,
            )
            for k, v in obj.items()
        }
    elif isinstance(obj, Sequence) and not isinstance(obj, str):
        obj = [
            _replace_refs(
                v,
                base_uri=base_uri,
                jsonschema=jsonschema,
                load_on_repr=load_on_repr,
                merge_props=merge_props,
                store=store,
                path=path + (i,),
                recursing=True,
            )
            for i, v in enumerate(obj)
        ]

    # If this object itself was a reference, replace it with a JsonRef
    if isinstance(obj, Mapping) and isinstance(obj.get("$ref"), str):
        obj = JsonRef(
            obj,
            base_uri=base_uri,
            jsonschema=jsonschema,
            load_on_repr=load_on_repr,
            merge_props=merge_props,
            _path=path,
            _store=store,
        )

    # Store the document with all references replaced in our cache
    if store_uri is not None:
        store[store_uri] = obj

    return obj


def _ref_encoder_factory(cls):
    class JSONRefEncoder(cls):
        def default(self, o):
            if hasattr(o, "__reference__"):
                return o.__reference__
            return super(JSONRefEncoder, cls).default(o)

        # Python 2.6 doesn't work with the default method
        def _iterencode(self, o, *args, **kwargs):
            if hasattr(o, "__reference__"):
                o = o.__reference__
            return super(JSONRefEncoder, self)._iterencode(o, *args, **kwargs)

        # Pypy doesn't work with either of the other methods
        def _encode(self, o, *args, **kwargs):
            if hasattr(o, "__reference__"):
                o = o.__reference__
            return super(JSONRefEncoder, self)._encode(o, *args, **kwargs)

    return JSONRefEncoder
