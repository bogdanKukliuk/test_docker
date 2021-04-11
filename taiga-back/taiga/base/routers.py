# -*- coding: utf-8 -*-
# Copyright (C) 2014-present Taiga Agile LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Django Rest Framework 2.4.0 routers module (should be removed when 2.4 is released)

import itertools
from collections import namedtuple
from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, URLResolver

from taiga.base.api import views
from taiga.base import response
from taiga.base.api.reverse import reverse
from taiga.base.api.urlpatterns import format_suffix_patterns


Route = namedtuple('Route', ['url', 'mapping', 'name', 'initkwargs'])
DynamicDetailRoute = namedtuple('DynamicDetailRoute', ['url', 'name', 'initkwargs'])
DynamicListRoute = namedtuple('DynamicListRoute', ['url', 'name', 'initkwargs'])


def replace_methodname(format_string, methodname):
    """
    Partially format a format_string, swapping out any
    '{methodname}' or '{methodnamehyphen}' components.
    """
    methodnamehyphen = methodname.replace('_', '-')
    ret = format_string
    ret = ret.replace('{methodname}', methodname)
    ret = ret.replace('{methodnamehyphen}', methodnamehyphen)
    return ret


def flatten(list_of_lists):
    """
    Takes an iterable of iterables, returns a single iterable containing all items
    """
    return itertools.chain(*list_of_lists)


class BaseRouter(object):
    def __init__(self):
        self.registry = []

    def register(self, prefix, viewset, base_name=None):
        if base_name is None:
            base_name = self.get_default_base_name(viewset)
        self.registry.append((prefix, viewset, base_name))

    def get_default_base_name(self, viewset):
        """
        If `base_name` is not specified, attempt to automatically determine
        it from the viewset.
        """
        raise NotImplemented('get_default_base_name must be overridden')

    def get_urls(self):
        """
        Return a list of URL patterns, given the registered viewsets.
        """
        raise NotImplemented('get_urls must be overridden')

    @property
    def urls(self):
        if not hasattr(self, '_urls'):
            self._urls = self.get_urls()
        return self._urls


class SimpleRouter(BaseRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    def __init__(self, trailing_slash=True):
        self.trailing_slash = trailing_slash and '/' or ''
        super(SimpleRouter, self).__init__()

    def get_default_base_name(self, viewset):
        """
        If `base_name` is not specified, attempt to automatically determine
        it from the viewset.
        """
        model_cls = getattr(viewset, 'model', None)
        queryset = getattr(viewset, 'queryset', None)
        if model_cls is None and queryset is not None:
            model_cls = queryset.model

        assert model_cls, '`base_name` argument not specified, and could ' \
            'not automatically determine the name from the viewset, as ' \
            'it does not have a `.model` or `.queryset` attribute.'

        return model_cls._meta.object_name.lower()

    def get_routes(self, viewset):
        """
        Augment `self.routes` with any dynamically generated routes.

        Returns a list of the Route namedtuple.
        """

        known_actions = flatten([route.mapping.values() for route in self.routes if isinstance(route, Route)])

        # Determine any `@detail_route` or `@list_route` decorated methods on the viewset
        detail_routes = []
        list_routes = []
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            httpmethods = getattr(attr, 'bind_to_methods', None)
            detail = getattr(attr, 'detail', True)
            if httpmethods:
                if methodname in known_actions:
                    raise ImproperlyConfigured('Cannot use @detail_route or @list_route '
                                               'decorators on method "%s" '
                                               'as it is an existing route' % methodname)
                httpmethods = [method.lower() for method in httpmethods]
                if detail:
                    detail_routes.append((httpmethods, methodname))
                else:
                    list_routes.append((httpmethods, methodname))

        ret = []
        for route in self.routes:
            if isinstance(route, DynamicDetailRoute):
                # Dynamic detail routes (@detail_route decorator)
                for httpmethods, methodname in detail_routes:
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(getattr(viewset, methodname).kwargs)
                    ret.append(Route(
                        url=replace_methodname(route.url, methodname),
                        mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                        name=replace_methodname(route.name, methodname),
                        initkwargs=initkwargs,
                    ))
            elif isinstance(route, DynamicListRoute):
                # Dynamic list routes (@list_route decorator)
                for httpmethods, methodname in list_routes:
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(getattr(viewset, methodname).kwargs)
                    ret.append(Route(
                        url=replace_methodname(route.url, methodname),
                        mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                        name=replace_methodname(route.name, methodname),
                        initkwargs=initkwargs,
                    ))
            else:
                # Standard route
                ret.append(route)

        return ret

    def get_method_map(self, viewset, method_map):
        """
        Given a viewset, and a mapping of http methods to actions,
        return a new mapping which only includes any mappings that
        are actually implemented by the viewset.
        """
        bound_methods = {}
        for method, action in method_map.items():
            if hasattr(viewset, action):
                bound_methods[method] = action
        return bound_methods

    def get_lookup_regex(self, viewset, lookup_prefix=''):
        """
        Given a viewset, return the portion of URL regex that is used
        to match against a single instance.

        Note that lookup_prefix is not used directly inside REST rest_framework
        itself, but is required in order to nicely support nested router
        implementations, such as drf-nested-routers.

        https://github.com/alanjds/drf-nested-routers
        """
        base_regex = '(?P<{lookup_prefix}{lookup_field}>{lookup_value})'
        # Use `pk` as default field, unset set.  Default regex should not
        # consume `.json` style suffixes and should break at '/' boundaries.
        lookup_field = getattr(viewset, 'lookup_field', 'pk')
        lookup_value = getattr(viewset, 'lookup_value_regex', '[^/.]+')
        return base_regex.format(
            lookup_prefix=lookup_prefix,
            lookup_field=lookup_field,
            lookup_value=lookup_value
        )

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        ret = []

        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                # Build the url pattern
                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )
                view = viewset.as_view(mapping, **route.initkwargs)
                name = route.name.format(basename=basename)
                ret.append(url(regex, view, name=name))

        return ret


class DRFDefaultRouter(SimpleRouter):
    """
    The default router extends the SimpleRouter, but also adds in a default
    API root view, and adds format suffix patterns to the URLs.
    """
    include_root_view = True
    include_format_suffixes = True
    root_view_name = 'api-root'

    def get_api_root_view(self):
        """
        Return a view to use as the API root.
        """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        class APIRoot(views.APIView):
            _ignore_model_permissions = True

            def get(self, request, format=None):
                ret = {}
                for key, url_name in api_root_dict.items():
                    try:
                        ret[key] = reverse(url_name, request=request, format=format)
                    except NoReverseMatch:
                        # Support resources that are prefixed by a parametrized url
                        ret[key] = request.build_absolute_uri() + key
                return response.Response(ret)

        return APIRoot.as_view()

    def get_urls(self):
        """
        Generate the list of URL patterns, including a default root view
        for the API, and appending `.json` style format suffixes.
        """
        urls = []

        if self.include_root_view:
            root_url = url(r'^$', self.get_api_root_view(), name=self.root_view_name)
            urls.append(root_url)

        default_urls = super(DRFDefaultRouter, self).get_urls()
        urls.extend(default_urls)

        if self.include_format_suffixes:
            urls = format_suffix_patterns(urls)

        return urls


class NestedRegistryItem(object):
    def __init__(self, router, parent_prefix, parent_item=None):
        self.router = router
        self.parent_prefix = parent_prefix
        self.parent_item = parent_item

    def register(self, prefix, viewset, base_name, parents_query_lookups):
        self.router._register(
            prefix=self.get_prefix(current_prefix=prefix, parents_query_lookups=parents_query_lookups),
            viewset=viewset,
            base_name=base_name,
        )
        return NestedRegistryItem(
            router=self.router,
            parent_prefix=prefix,
            parent_item=self
        )

    def get_prefix(self, current_prefix, parents_query_lookups):
        return "{0}/{1}".format(
            self.get_parent_prefix(parents_query_lookups),
            current_prefix
        )

    def get_parent_prefix(self, parents_query_lookups):
        prefix = "/"
        current_item = self
        i = len(parents_query_lookups) - 1
        while current_item:
            prefix = "{parent_prefix}/(?P<{parent_pk_kwarg_name}>[^/.]+)/{prefix}".format(
                parent_prefix=current_item.parent_prefix,
                parent_pk_kwarg_name=parents_query_lookups[i],
                prefix=prefix
            )
            i -= 1
            current_item = current_item.parent_item
        return prefix.strip("/")


class NestedRouterMixin:
    def _register(self, *args, **kwargs):
        return super().register(*args, **kwargs)

    def register(self, *args, **kwargs):
        self._register(*args, **kwargs)
        return NestedRegistryItem(
            router=self,
            parent_prefix=self.registry[-1][0]
        )


class DefaultRouter(NestedRouterMixin, DRFDefaultRouter):
    pass

__all__ = ["DefaultRouter"]
