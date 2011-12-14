from tempest import openstack
from tempest.common.utils.data_utils import rand_name
import unittest2 as unittest


class ServerMetadataTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.os = openstack.Manager()
        cls.client = cls.os.servers_client
        cls.config = cls.os.config
        cls.image_ref = cls.config.env.image_ref
        cls.flavor_ref = cls.config.env.flavor_ref

        #Create a server to be used for all read only tests
        name = rand_name('server')
        resp, server = cls.client.create_server(name, cls.image_ref,
                                                cls.flavor_ref, meta={})
        cls.server_id = server['id']

        #Wait for the server to become active
        cls.client.wait_for_server_status(cls.server_id, 'ACTIVE')

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_server(cls.server_id)

    def setUp(self):
        meta = {'key1': 'value1', 'key2': 'value2'}
        resp, _ = self.client.set_server_metadata(self.server_id, meta)
        self.assertEqual(resp.status, 200)

    def test_list_server_metadata(self):
        """All metadata key/value pairs for a server should be returned"""
        resp, resp_metadata = self.client.list_server_metadata(self.server_id)

        #Verify the expected metadata items are in the list
        self.assertEqual(200, resp.status)
        expected = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(expected, resp_metadata)

    def test_set_server_metadata(self):
        """The server's metadata should be replaced with the provided values"""
        #Create a new set of metadata for the server
        req_metadata = {'meta2': 'data2', 'meta3': 'data3'}
        resp, metadata = self.client.set_server_metadata(self.server_id,
                                                         req_metadata)
        self.assertEqual(200, resp.status)

        #Verify the expected values are correct, and that the
        #previous values have been removed
        resp, resp_metadata = self.client.list_server_metadata(self.server_id)
        self.assertEqual(resp_metadata, req_metadata)

    def test_update_server_metadata(self):
        """
        The server's metadata values should be updated to the
        provided values
        """
        meta = {'key1': 'alt1', 'key3': 'value3'}
        resp, metadata = self.client.update_server_metadata(self.server_id,
                                                            meta)
        self.assertEqual(200, resp.status)

        #Verify the values have been updated to the proper values
        resp, resp_metadata = self.client.list_server_metadata(self.server_id)
        expected = {'key1': 'alt1', 'key2': 'value2', 'key3': 'value3'}
        self.assertEqual(expected, resp_metadata)

    def test_get_server_metadata_item(self):
        """ The value for a specic metadata key should be returned """
        resp, meta = self.client.get_server_metadata_item(self.server_id,
                                                          'key2')
        self.assertTrue('value2', meta['key2'])

    def test_set_server_metadata_item(self):
        """The item's value should be updated to the provided value"""
        #Update the metadata value
        meta = {'nova': 'alt'}
        resp, body = self.client.set_server_metadata_item(self.server_id,
                                                          'nova', meta)
        self.assertEqual(200, resp.status)

        #Verify the meta item's value has been updated
        resp, resp_metadata = self.client.list_server_metadata(self.server_id)
        expected = {'key1': 'value1', 'key2': 'value2', 'nova': 'alt'}
        self.assertEqual(expected, resp_metadata)

    def test_delete_server_metadata_item(self):
        """The metadata value/key pair should be deleted from the server"""
        resp, meta = self.client.delete_server_metadata_item(self.server_id,
                                                             'key1')
        self.assertEqual(204, resp.status)

        #Verify the metadata item has been removed
        resp, resp_metadata = self.client.list_server_metadata(self.server_id)
        expected = {'key2': 'value2'}
        self.assertEqual(expected, resp_metadata)
