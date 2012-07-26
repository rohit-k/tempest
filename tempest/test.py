# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import time

import unittest2 as unittest

from tempest import manager
from tempest.tests.compute.base import BaseComputeTest

LOG = logging.getLogger(__name__)


class TestCase(unittest.TestCase):

    """
    Base test case class for all Tempest tests

    Contains basic setup and convenience methods
    """

    resource_keys = {}
    resources = []
    manager_class = None

    @classmethod
    def setUpClass(cls):
        cls.manager = cls.manager_class()
        cls.config = cls.manager.config
        cls.client = cls.manager.client

    def set_resource(self, key, thing):
        LOG.debug("Adding %r to shared resources of %s" %
                  (thing, self.__class__.__name__))
        self.resource_keys[key] = thing
        self.resources.append(thing)

    def get_resource(self, key):
        return self.resource_keys[key]

    def remove_resource(self, key):
        thing = self.resource_keys[key]
        self.resources.remove(thing)
        del self.resource_keys[key]


class ComputeDefaultClientTest(TestCase):

    """
    Base test case class for OpenStack Compute API (Nova)
    that uses the novaclient libs for calling the API.
    """

    manager_class = manager.ComputeDefaultClientManager

    def status_timeout(self, things, thing_id, expected_status):
        """
        Given a thing and an expected status, do a loop, sleeping
        for a configurable amount of time, checking for the
        expected status to show. At any time, if the returned
        status of the thing is ERROR, fail out.
        """
        now = time.time()
        timeout = now + self.config.compute.build_timeout
        sleep_for = self.config.compute.build_interval
        while now < timeout:
            # python-novaclient has resources available to its client
            # that all implement a get() method taking an identifier
            # for the singular resource to retrieve.
            thing = things.get(thing_id)
            new_status = thing.status
            if new_status == 'ERROR':
                self.fail("%s failed to get to expected status."
                          "In ERROR state."
                          % thing)
            elif new_status == expected_status:
                return  # All good.
            LOG.debug("Waiting for %s to get to %s status. "
                      "Currently in %s status",
                      thing, expected_status, new_status)
            LOG.debug("Sleeping for %d seconds", sleep_for)
        self.fail("Timed out waiting for thing %s to become %s"
                  % (thing_id, expected_status))


class ComputeFuzzClientTest(TestCase, BaseComputeTest):

    """
    Base test case class for OpenStack Compute API (Nova)
    that uses the Tempest REST fuzz client libs for calling the API.
    """

    manager_class = manager.ComputeFuzzClientManager

    def status_timeout(self, client_get_method, thing_id, expected_status):
        """
        Given a method to get a resource and an expected status, do a loop,
        sleeping for a configurable amount of time, checking for the
        expected status to show. At any time, if the returned
        status of the thing is ERROR, fail out.

        :param client_get_method: The callable that will retrieve the thing
                                  with ID :param:thing_id
        :param thing_id: The ID of the thing to get
        :param expected_status: String value of the expected status of the
                                thing that we are looking for.

        :code ..

            Usage:

            def test_some_server_action(self):
                client = self.servers_client
                resp, server = client.create_server('random_server')
                self.status_timeout(client.get_server, server['id'], 'ACTIVE')
        """
        now = time.time()
        timeout = now + self.config.compute.build_timeout
        sleep_for = self.config.compute.build_interval
        while now < timeout:
            # Tempest REST client has resources available to its client
            # that all implement a various get_$resource() methods taking
            # an identifier for the singular resource to retrieve.
            thing = client_get_method(thing_id)
            new_status = thing['status']
            if new_status == 'ERROR':
                self.fail("%s failed to get to expected status."
                          "In ERROR state."
                          % thing)
            elif new_status == expected_status:
                return  # All good.
            LOG.debug("Waiting for %s to get to %s status. "
                      "Currently in %s status",
                      thing, expected_status, new_status)
            LOG.debug("Sleeping for %d seconds", sleep_for)
        self.fail("Timed out waiting for thing %s to become %s"
                  % (thing_id, expected_status))
