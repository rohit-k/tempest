from nose.plugins.attrib import attr
import unittest2 as unittest

from tempest.common.utils.data_utils import rand_name
import tempest.config
from tempest import openstack


def _parse_image_id(image_ref):
    temp = image_ref.rsplit('/')
    return temp[6]


class ImagesTest(unittest.TestCase):

    create_image_enabled = tempest.config.TempestConfig().\
            env.create_image_enabled

    @classmethod
    def setUpClass(cls):
        cls.os = openstack.Manager()
        cls.client = cls.os.images_client
        cls.servers_client = cls.os.servers_client
        cls.config = cls.os.config
        cls.image_ref = cls.config.env.image_ref
        cls.flavor_ref = cls.config.env.flavor_ref
        cls.create_image_enabled = cls.config.env.create_image_enabled

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

        #Create a new image
        name = rand_name('image')
        meta = {'image_type': 'test'}
        resp, body = self.client.create_image(server['id'], name, meta)
        image_id = _parse_image_id(resp['location'])
        self.client.wait_for_image_resp_code(image_id, 200)
        self.client.wait_for_image_status(image_id, 'ACTIVE')

        #Verify the image was created correctly
        resp, image = self.client.get_image(image_id)
        self.assertEqual(name, image['name'])
        self.assertEqual('test', image['metadata']['image_type'])

        #Verify minRAM and minDisk values are the same as the original image
        resp, original_image = self.client.get_image(self.image_ref)
        self.assertEqual(original_image['minRam'], image['minRam'])
        self.assertEqual(original_image['minDisk'], image['minDisk'])

        #Teardown
        self.client.delete_image(image['id'])
        self.servers_client.delete_server(server['id'])
