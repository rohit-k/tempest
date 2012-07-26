import nose
from tempest import exceptions
from tempest import whitebox
from tempest.tests.identity.base import BaseIdentityAdminTest
from nose.plugins.attrib import attr


@attr(type='whitebox')
class ServersWhiteboxTest(whitebox.ComputeWhiteboxTest):

    @classmethod
    def setUpClass(cls):
        super(ServersWhiteboxTest, cls).setUpClass()
        BaseIdentityAdminTest.setUpClass()
        cls.client = cls.servers_client
        cls.img_client = cls.images_client
        cls.admin_client = BaseIdentityAdminTest.client

        cls.connection, cls.meta = cls.get_db_handle_and_meta()
        if not whitebox.WHITEBOX_DB_AVAILABLE:
            msg = "Skipping tests - Connection to database not available"
            raise nose.SkipTest(msg)

        resp, tenants = cls.admin_client.list_tenants()
        cls.tenant_id = [tnt['id'] for tnt in tenants if tnt['name'] ==
                        cls.config.compute.tenant_name][0]

        cls.shared_server = cls.create_server()

    def tearDown(cls):
        for server in cls.servers:
            try:
                cls.client.delete_server(server['id'])
            except exceptions.NotFound:
                continue

    def test_create_server_vcpu_quota_full(self):
        """Disallow server creation when tenant's vcpu quota is full"""
        quotas = self.meta.tables['quotas']
        stmt = quotas.select().where(
                              quotas.c.project_id == self.tenant_id).where(
                              quotas.c.resource == 'cores')
        result = self.connection.execute(stmt).first()

        # Set vcpu quota for tenant if not already set
        if not result:
            cores_hard_limit = 2
            stmt = quotas.insert().values(deleted=0,
                                project_id=self.tenant_id, resource='cores',
                                hard_limit=cores_hard_limit)

            self.connection.execute(stmt, autocommit=True)
        else:
            cores_hard_limit = result.hard_limit

        # Create servers assuming 1 VCPU per instance i.e flavor_id=1
        try:
            for count in range(cores_hard_limit + 1):
                self.create_server()
        except exceptions.OverLimit:
            pass
        else:
            self.fail("Could create servers over the VCPU quota limit")
        finally:
            stmt = quotas.delete()
            self.connection.execute(stmt, autocommit=True)

    def test_create_server_memory_quota_full(self):
        """Disallow server creation when tenant's memory quota is full"""
        quotas = self.meta.tables['quotas']
        stmt = quotas.select().where(
                              quotas.c.project_id == self.tenant_id).where(
                              quotas.c.resource == 'ram')
        result = self.connection.execute(stmt).first()

        # Set memory quota for tenant if not already set
        if not result:
            ram_hard_limit = 1024
            stmt = quotas.insert().values(deleted=0,
                                project_id=self.tenant_id, resource='ram',
                                hard_limit=ram_hard_limit)

            self.connection.execute(stmt, autocommit=True)
        else:
            ram_hard_limit = result.hard_limit

        try:
            # Set a hard range of 3 servers for reaching the RAM quota
            for count in range(3):
                self.create_server()
        except exceptions.OverLimit:
            pass
        else:
            self.fail("Could create servers over the RAM quota limit")
        finally:
            stmt = quotas.delete()
            self.connection.execute(stmt, autocommit=True)

    def update_state(self, server_id, vm_state, task_state, deleted=0):
        """Update states of an instance in database for validation"""
        if not task_state:
            task_state = 'NULL'

        instances = self.meta.tables['instances']
        stmt = instances.update().where(instances.c.uuid == server_id).values(
                                                               deleted=deleted,
                                                             vm_state=vm_state,
                                                         task_state=task_state)
        self.connection.execute(stmt, autocommit=True)

    def _test_delete_server_base(self, vm_state, task_state):
        """
        Base method for delete server tests based on vm and task states.
        Validates for successful server termination.
        """
        try:
            server = self.create_server()
            self.update_state(server['id'], vm_state, task_state)

            resp, body = self.client.delete_server(server['id'])
            self.assertEqual('204', resp['status'])
            self.client.wait_for_server_termination(server['id'],
                                              initial_status=vm_state.upper())

            instances = self.meta.tables['instances']
            stmt = instances.select().where(instances.c.uuid == server['id'])
            result = self.connection.execute(stmt).first()

            self.assertEqual(1, result.deleted)
            self.assertEqual('deleted', result.vm_state)
            self.assertEqual(None, result.task_state)
        except:
            raise
            self.fail("Should be able to delete a server when vm_state=%s and "
                      "task_state=%s" % (vm_state, task_state))

    def _test_delete_server_403_base(self, vm_state, task_state):
        """
        Base method for delete server tests based on vm and task states.
        Validates for 403 error code.
        """
        try:
            self.update_state(self.shared_server['id'], vm_state, task_state)

            self.assertRaises(exceptions.Unauthorized,
                           self.client.delete_server, self.shared_server['id'])
        except:
            self.fail("Should not allow delete server when vm_state=%s and "
                    "task_state=%s" % (vm_state, task_state))
        finally:
            self.update_state(self.shared_server['id'], 'active', None)

    def test_delete_server_when_vm_eq_building_task_eq_networking(self):
        """Delete server when instance states are building,networking"""
        self._test_delete_server_base('building', 'networking')

    def test_delete_server_when_vm_eq_building_task_eq_bdm(self):
        """
        Delete server when instance states are building,block device mapping
        """
        self._test_delete_server_base('building', 'block_device_mapping')

    def test_delete_server_when_vm_eq_building_task_eq_spawning(self):
        """Delete server when instance states are building,spawning"""
        self._test_delete_server_base('building', 'spawning')

    def test_delete_server_when_vm_eq_active_task_eq_image_backup(self):
        """Delete server when instance states are active,image_backup"""
        self._test_delete_server_base('active', 'image_backup')

    def test_delete_server_when_vm_eq_active_task_eq_rebuilding(self):
        """Delete server when instance states are active,rebuilding"""
        self._test_delete_server_base('active', 'rebuilding')

    def test_delete_server_when_vm_eq_error_task_eq_spawning(self):
        """Delete server when instance states are error,spawning"""
        self._test_delete_server_base('error', 'spawning')

    def test_delete_server_when_vm_eq_resized_task_eq_resize_prep(self):
        """Delete server when instance states are resized,resize_prep"""
        self._test_delete_server_403_base('resized', 'resize_prep')

    def test_delete_server_when_vm_eq_resized_task_eq_resize_migrating(self):
        """Delete server when instance states are resized,resize_migrating"""
        self._test_delete_server_403_base('resized', 'resize_migrating')

    def test_delete_server_when_vm_eq_resized_task_eq_resize_migrated(self):
        """Delete server when instance states are resized,resize_migrated"""
        self._test_delete_server_403_base('resized', 'resize_migrated')

    def test_delete_server_when_vm_eq_resized_task_eq_resize_finish(self):
        """Delete server when instance states are resized,resize_finish"""
        self._test_delete_server_403_base('resized', 'resize_finish')

    def test_delete_server_when_vm_eq_resized_task_eq_resize_reverting(self):
        """Delete server when instance states are resized,resize_reverting"""
        self._test_delete_server_403_base('resized', 'resize_reverting')

    def test_delete_server_when_vm_eq_resized_task_eq_resize_confirming(self):
        """Delete server when instance states are resized,resize_confirming"""
        self._test_delete_server_403_base('resized', 'resize_confirming')

    def test_delete_server_when_vm_eq_active_task_eq_resize_verify(self):
        """Delete server when instance states are active,resize_verify"""
        self._test_delete_server_base('active', 'resize_verify')

    def test_delete_server_when_vm_eq_active_task_eq_rebooting(self):
        """Delete server when instance states are active,rebooting"""
        self._test_delete_server_base('active', 'rebooting')

    def test_delete_server_when_vm_eq_building_task_eq_deleting(self):
        """Delete server when instance states are building,deleting"""
        self._test_delete_server_base('building', 'deleting')

    def test_delete_server_when_vm_eq_active_task_eq_deleting(self):
        """Delete server when instance states are active,deleting"""
        self._test_delete_server_base('active', 'deleting')

    def test_delete_server_when_vm_eq_error_task_eq_none(self):
        """Delete server when instance states are error,None"""
        self._test_delete_server_base('error', None)

    def test_delete_server_when_vm_eq_resized_task_eq_none(self):
        """Delete server when instance states are resized,None"""
        self._test_delete_server_403_base('resized', None)

    def test_delete_server_when_vm_eq_error_task_eq_resize_prep(self):
        """Delete server when instance states are error,resize_prep"""
        self._test_delete_server_base('error', 'resize_prep')

    def test_delete_server_when_vm_eq_error_task_eq_error(self):
        """Delete server when instance states are error,error"""
        self._test_delete_server_base('error', 'error')
