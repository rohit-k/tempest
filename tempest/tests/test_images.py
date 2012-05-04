from nose.plugins.attrib import attr
import unittest2 as unittest

from tempest.common.utils.data_utils import rand_name
from base_compute_test import BaseComputeTest
import tempest.config
from tempest import openstack


def _parse_image_id(image_ref):
    temp = image_ref.rsplit('images/')
    return temp[1]


class ImagesTest(BaseComputeTest):

    create_image_enabled = tempest.config.TempestConfig().\
            compute.create_image_enabled

    @classmethod
    def setUpClass(cls):
        cls.client = cls.images_client
        cls.servers_client = cls.servers_client
        cls.create_image_enabled = cls.config.compute.create_image_enabled

    @attr(type='smoke')
    @unittest.skipUnless(create_image_enabled,
                         'Environment unable to create images.')
    def test_create_delete_image(self):
        """An image for the provided server should be created"""
        server_name = rand_name('server')
        resp, server = self.servers_client.create_server(server_name,
                                                         self.image_ref,
                                                         self.flavor_ref)
        self.servers_client.wait_for_server_status(server['id'], 'ACTIVE')

        # Create a new image
        name = rand_name('image')
        meta = {'image_type': 'test'}
        resp, body = self.client.create_image(server['id'], name, meta)
        image_id = _parse_image_id(resp['location'])
        self.client.wait_for_image_resp_code(image_id, 200)
        self.client.wait_for_image_status(image_id, 'ACTIVE')

        # Verify the image was created correctly
        resp, image = self.client.get_image(image_id)
        self.assertEqual(name, image['name'])
        self.assertEqual('test', image['metadata']['image_type'])

        # Verify minRAM and minDisk values are the same as the original image
        resp, original_image = self.client.get_image(self.image_ref)
        self.assertEqual(original_image['minRam'], image['minRam'])
        self.assertEqual(original_image['minDisk'], image['minDisk'])

        # Teardown
        self.client.delete_image(image['id'])
        self.servers_client.delete_server(server['id'])

    @attr(type='negative')
    def test_create_image_from_deleted_server(self):
        """An image should not be created if the server instance is removed """
        server_name = rand_name('server')
        resp, server = self.servers_client.create_server(server_name,
                                                         self.image_ref,
                                                         self.flavor_ref)
        self.servers_client.wait_for_server_status(server['id'], 'ACTIVE')

        # Delete server before trying to create server
        self.servers_client.delete_server(server['id'])

        try:
            # Create a new image after server is deleted
            name = rand_name('image')
            meta = {'image_type': 'test'}
            resp, body = self.client.create_image(server['id'], name, meta)

        except:
            pass

        else:
            image_id = _parse_image_id(resp['location'])
            self.client.wait_for_image_resp_code(image_id, 200)
            self.client.wait_for_image_status(image_id, 'ACTIVE')
            self.client.delete_image(image_id)
            self.fail("Should not create snapshot from deleted instance!")
