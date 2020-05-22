# coding=utf-8
import requests
import os.path

from megaoptim import *


class Client(object):

    def __init__(self, api_key=None):
        if api_key is None:
            raise Exception('Please provide MegaOptim.com API key')
        self.api_key = api_key
        self.api_base_url = 'https://api.megaoptim.com/v1/'
        self.api_optimize_url = self.api_base_url + 'optimize'
        self.api_user_agent = 'MegaOptim Python Client v1.0.0'
        self.api_headers = {'User-Agent': self.api_user_agent, 'X-API-KEY': self.api_key}

    def get_result(self, job_id, timeout=300):
        if job_id is None:
            raise Exception('Please provide valid MegaOptim process id. Process ID is returned after you call the '
                                '/optimize endpoint and your job has been queued for processing.')
        results_endpoint = self.api_optimize_url + '/' + job_id + '/result?timeout=' + str(timeout)

        r = requests.post(url=results_endpoint, headers=self.api_headers)
        if r.ok:
            return r.json()
        else:
            try:
                return r.json()
            except Exception as e:
                raise Exception('Failed to parse JSON response from MegaOptim.com API')

    def send(self, resource=None, params=None):
        help = 'Invalid resouce type. Resource must be valid image. Also it should any of the following: image url, ' \
               'local image path, tuple of up to 5 image urls or tuple of up to 5 local image paths. '
        if resource is None:
            raise Exception('Please provide a valid file path to the image')
        if params is None:
            raise Exception('Please provide image optimization parameters')
        if not isinstance(params, dict):
            raise Exception('The parameter \'params\' must be of typ dict')

        params = maybe_set_default('compression', 'intelligent', params)
        params = maybe_set_default('keep_exif', '1', params)
        params = maybe_set_default('cmyktorgb', '1', params)
        params = maybe_set_default('max_width', '0', params)
        params = maybe_set_default('max_height', '0', params)

        files = dict()
        if isinstance(resource, tuple):
            if len(resource) > 5 or len(resource) < 1:
                raise Exception(help)
            else:
                valid_files = False
                valid_urls = all(validate_url(item) for item in resource)
                if not valid_urls:
                    valid_files = all(os.path.isfile(item) for item in resource)
                if valid_urls:
                    for i, item in enumerate(resource):
                        no = (i + 1)
                        index = 'url' + str(no)
                        params[index] = item
                    params['type'] = 'urls'
                elif valid_files:
                    for i, item in enumerate(resource):
                        no = (i + 1)
                        index = 'file' + str(no)
                        files[index] = get_file(item)
                    params['type'] = 'files'
                else:
                    raise Exception(help)
        else:
            if validate_url(resource):
                params['url'] = resource
                params['type'] = 'url'
            elif os.path.isfile(resource):
                files['file'] = get_file(resource)
                params['type'] = 'file'
            else:
                raise Exception(help)

        requires_upload = params['type'] == 'file' or params['type'] == 'files'
        if requires_upload:
            r = requests.post(url=self.api_optimize_url, headers=self.api_headers, files=files, data=params)
        else:
            r = requests.post(url=self.api_optimize_url, headers=self.api_headers, data=params)

        if r.ok:
            return r.json()
        else:
            try:
                return r.json()
            except Exception as e:
                raise Exception('Failed to parse JSON response from MegaOptim.com API')

    def optimize(self, resource, params, timeout=300):
        result = self.send(resource, params)
        if result.get('status') == 'processing':
            if 'callback_url' in params and params['callback_url'] is not None:
                return result
            else:
                process_id = result.get('process_id')
                return self.get_result(process_id, timeout)
        else:
            raise Exception(result.get('errors'))
