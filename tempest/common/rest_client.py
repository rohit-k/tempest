import json

import httplib2

from tempest import exceptions
import tempest.config


class RestClient(object):

    def __init__(self, config, user, key, auth_url, tenant_name=None):
        self.config = config
        if self.config.env.authentication == 'keystone_v2':
            self.token, self.base_url = self.keystone_v2_auth(user,
                                                              key,
                                                              auth_url,
                                                              tenant_name)
        else:
            self.token, self.base_url = self.basic_auth(user,
                                                        key,
                                                        auth_url)

    def basic_auth(self, user, api_key, auth_url):
        """
        Provides authentication for the target API
        """

        params = {}
        params['headers'] = {'User-Agent': 'Test-Client', 'X-Auth-User': user,
                             'X-Auth-Key': api_key}

        self.http_obj = httplib2.Http()
        resp, body = self.http_obj.request(auth_url, 'GET', **params)
        try:
            return resp['x-auth-token'], resp['x-server-management-url']
        except:
            raise

    def keystone_v2_auth(self, user, api_key, auth_url, tenant_name):
        """
        Provides authentication via Keystone 2.0
        """

        creds = {'auth': {
                'passwordCredentials': {
                    'username': user,
                    'password': api_key,
                },
                'tenantName': tenant_name
            }
        }

        self.http_obj = httplib2.Http()
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(creds)
        resp, body = self.http_obj.request(auth_url, 'POST',
                                           headers=headers, body=body)

        if resp.status == 200:
            try:
                auth_data = json.loads(body)['access']
                token = auth_data['token']['id']
                endpoints = auth_data['serviceCatalog'][0]['endpoints']
                mgmt_url = endpoints[0]['publicURL']

                #TODO (dwalleck): This is a horrible stopgap.
                #Need to join strings more cleanly
                temp = mgmt_url.rsplit('/')
                service_url = temp[0] + '//' + temp[2] + '/' + temp[3] + '/'
                management_url = service_url + tenant_name
                return token, management_url
            except Exception, e:
                print "Failed to authenticate user: %s" % e
                raise
        elif resp.status == 401:
            raise exceptions.AuthenticationFailure(user=user, password=api_key)

    def post(self, url, body, headers):
        return self.request('POST', url, headers, body)

    def get(self, url):
        return self.request('GET', url)

    def delete(self, url):
        return self.request('DELETE', url)

    def put(self, url, body, headers):
        return self.request('PUT', url, headers, body)

    def request(self, method, url, headers=None, body=None):
        """A simple HTTP request interface."""

        self.http_obj = httplib2.Http()
        if headers == None:
            headers = {}
        headers['X-Auth-Token'] = self.token

        req_url = "%s/%s" % (self.base_url, url)
        resp, body = self.http_obj.request(req_url, method,
                                           headers=headers, body=body)
        if resp.status == 400:
            body = json.loads(body)
            raise exceptions.BadRequest(body['badRequest']['message'])

        if resp.status == 413:
            body = json.loads(body)
            raise exceptions.OverLimit(body['overLimit']['message'])

        if resp.status in (500, 501):
            body = json.loads(body)
            raise exceptions.ComputeFault(body['computeFault']['message'])

        return resp, body
