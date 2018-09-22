# coding=utf-8

import os

from megaoptim import Client

# Init MegaOptim API client
api = Client("_YOUR_API_KEY_")
try:
    # Pick up local path of the file
    file_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'images' + os.sep + '1.png'
    # Init empty params, will default to keep_exif=1, cmyktorgb=1, compression=lossy, max_height=0, max_width=0
    # You can specify your own in params too!
    params = dict()
    # When files are send for processing we are calling another endpoint to get the results.
    # This is timeout for that endpoint. If not results are available in the given
    # seconds then the request will be dropped.
    timeout = 300
    # Optimize the file
    r = api.optimize(file_path, params, timeout)
    if r.get('status') == 'ok' and r.get('code') == 200:
        for item in r.get('result'):
            print('Success: ' + str(item['success']))
            print('File Name: ' + str(item['file_name']))
            print('Original Size: ' + str(item['original_size']))
            print('Saved Percent: ' + str(item['saved_percent']))
            print('Saved Bytes: ' + str(item['saved_bytes']))
            print('Optimized Size: ' + str(item['optimized_size']))
            print('Download Url: ' + str(item['url']))
            print("")
    else:
        errors = r.get('errors')
        for error in errors:
            print(error)

except Exception as e:
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(e).__name__, e.args)
    print (message)
