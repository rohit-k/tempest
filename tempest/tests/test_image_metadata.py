from tempest import openstack
from tempest.common.utils.data_utils import rand_name
import unittest2 as unittest


class ImagesMetadataTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.os = openstack.Manager()
        cls.servers_client = cls.os.servers_client
        cls.client = cls.os.images_client
        cls.config = cls.os.config
        cls.image_ref = cls.config.env.image_ref
        cls.flavor_ref = cls.config.env.flavor_ref
        cls.ssh_timeout = cls.config.nova.ssh_timeout

        name = rand_name('server')
        resp, server = cls.servers_client.create_server(name, cls.image_ref,
                                                        cls.flavor_ref)
        cls.server_id = server['id']

        #Wait for the server to become active
        cls.servers_client.wait_for_server_status(cls.server_id, 'ACTIVE')

        # Snapshot the server once to save time
        name = rand_name('image')
        resp, _ = cls.client.create_image(cls.server_id, name, {})
        cls.image_id = resp['location'].rsplit('/', 1)[1]

        cls.client.wait_for_image_resp_code(cls.image_id, 200)
        cls.client.wait_for_image_status(cls.image_id, 'ACTIVE')

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_image(cls.image_id)
        cls.servers_client.delete_server(cls.server_id)

    def setUp(self):
        meta = {'key1': 'value1', 'key2': 'value2'}
        resp, _ = self.client.set_image_metadata(self.image_id, meta)
        self.assertEqual(resp.status, 200)

    def test_list_image_metadata(self):
        """All metadata key/value pairs for an image should be returned"""
        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        expected = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(expected, resp_metadata)

    def test_set_image_metadata(self):
        """The metadata for the image should match the new values"""
        req_metadata = {'meta2': 'value2', 'meta3': 'value3'}
        resp, body = self.client.set_image_metadata(self.image_id,
                                                    req_metadata)

        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        self.assertEqual(req_metadata, resp_metadata)

    def test_update_image_metadata(self):
        """The metadata for the image should match the updated values"""
        req_metadata = {'key1': 'alt1', 'key3': 'value3'}
        resp, metadata = self.client.update_image_metadata(self.image_id,
                                                           req_metadata)

        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        expected = {'key1': 'alt1', 'key2': 'value2', 'key3': 'value3'}
        self.assertEqual(expected, resp_metadata)

    def test_get_image_metadata_item(self):
        """The value for a specific metadata key should be returned"""
        resp, meta = self.client.get_image_metadata_item(self.image_id,
                                                         'key2')
        self.assertTrue('value2', meta['key2'])

    def test_set_image_metadata_item(self):
        """
        The value provided for the given meta item should be set for the image
        """
        meta = {'key1': 'alt'}
        resp, body = self.client.set_image_metadata_item(self.image_id,
                                                         'key1', meta)
        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        expected = {'key1': 'alt', 'key2': 'value2'}
        self.assertEqual(expected, resp_metadata)

    def test_delete_image_metadata_item(self):
        """The metadata value/key pair should be deleted from the image"""
        resp, body = self.client.delete_image_metadata_item(self.image_id,
                                                            'key1')
        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        expected = {'key2': 'value2'}
        self.assertEqual(expected, resp_metadata)
