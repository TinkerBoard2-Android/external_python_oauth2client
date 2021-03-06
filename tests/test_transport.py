# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httplib2
import mock
import unittest2

from oauth2client import client
from oauth2client import transport


class TestMemoryCache(unittest2.TestCase):

    def test_get_set_delete(self):
        cache = transport.MemoryCache()
        self.assertIsNone(cache.get('foo'))
        self.assertIsNone(cache.delete('foo'))
        cache.set('foo', 'bar')
        self.assertEqual('bar', cache.get('foo'))
        cache.delete('foo')
        self.assertIsNone(cache.get('foo'))


class Test_get_cached_http(unittest2.TestCase):

    def test_global(self):
        cached_http = transport.get_cached_http()
        self.assertIsInstance(cached_http, httplib2.Http)
        self.assertIsInstance(cached_http.cache, transport.MemoryCache)

    def test_value(self):
        cache = object()
        with mock.patch('oauth2client.transport._CACHED_HTTP', new=cache):
            result = transport.get_cached_http()
        self.assertIs(result, cache)


class Test_get_http_object(unittest2.TestCase):

    @mock.patch.object(httplib2, 'Http', return_value=object())
    def test_it(self, http_klass):
        result = transport.get_http_object()
        self.assertEqual(result, http_klass.return_value)


class Test__initialize_headers(unittest2.TestCase):

    def test_null(self):
        result = transport._initialize_headers(None)
        self.assertEqual(result, {})

    def test_copy(self):
        headers = {'a': 1, 'b': 2}
        result = transport._initialize_headers(headers)
        self.assertEqual(result, headers)
        self.assertIsNot(result, headers)


class Test__apply_user_agent(unittest2.TestCase):

    def test_null(self):
        headers = object()
        result = transport._apply_user_agent(headers, None)
        self.assertIs(result, headers)

    def test_new_agent(self):
        headers = {}
        user_agent = 'foo'
        result = transport._apply_user_agent(headers, user_agent)
        self.assertIs(result, headers)
        self.assertEqual(result, {'user-agent': user_agent})

    def test_append(self):
        orig_agent = 'bar'
        headers = {'user-agent': orig_agent}
        user_agent = 'baz'
        result = transport._apply_user_agent(headers, user_agent)
        self.assertIs(result, headers)
        final_agent = user_agent + ' ' + orig_agent
        self.assertEqual(result, {'user-agent': final_agent})


class Test_clean_headers(unittest2.TestCase):

    def test_no_modify(self):
        headers = {b'key': b'val'}
        result = transport.clean_headers(headers)
        self.assertIsNot(result, headers)
        self.assertEqual(result, headers)

    def test_cast_unicode(self):
        headers = {u'key': u'val'}
        header_bytes = {b'key': b'val'}
        result = transport.clean_headers(headers)
        self.assertIsNot(result, headers)
        self.assertEqual(result, header_bytes)

    def test_unicode_failure(self):
        headers = {u'key': u'\u2603'}
        with self.assertRaises(client.NonAsciiHeaderError):
            transport.clean_headers(headers)

    def test_cast_object(self):
        headers = {b'key': True}
        header_str = {b'key': b'True'}
        result = transport.clean_headers(headers)
        self.assertIsNot(result, headers)
        self.assertEqual(result, header_str)


class Test_wrap_http_for_auth(unittest2.TestCase):

    def test_wrap(self):
        credentials = object()
        http = mock.Mock()
        http.request = orig_req_method = object()
        result = transport.wrap_http_for_auth(credentials, http)
        self.assertIsNone(result)
        self.assertNotEqual(http.request, orig_req_method)
        self.assertIs(http.request.credentials, credentials)
