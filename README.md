# Official MegaOptim.com library for Python

This is official python client for working with the [MegaOptim.com](https://megaoptim.com) API.

The library implements the MegaOptim REST service for optimizing images. It is compatible with both Python 2 and 3 and can be used in any project by installing with `pip` command.

## Installation

```
pip install megaoptim
```

## Getting Started

To start using the MegaOptim Image Optimization service you will need to obtain API key from [MegaOptim.com](https://megaoptim.com). Once  you have the key you will be able to start using the service immediately.

## How to use 

You can optimize your images in several ways. The api supports any of those: single url, single local file path, multiple urls, multiple local file paths.

Using the url/s approach is great for images that are already in production or any other place on the Internet. The direct upload method is ideal for your own galleries that aren't public, your deployment process, build script or the on-the-fly processing of your user's uploads where you don't have the images available online yet.

If you provide url/urls this library will pass them to the API server and the API server will download the contents. If you provide local path/paths the library will upload them in the initial request using HTTP Post.

The API currently accepts the following parameters:


| Parameter 	    | Possible Values               	                                        |
|-------------------|---------------------------------------------------------------------------|
| `compression`     | `intelligent`, `ultra` or `lossless` (default: `intelligent`)             |
| `type`        	| `url`, `urls`, `file`, `files`. `file/s` are local paths                  |
| `cmyktorgb`   	| `1` or `0` (default: `1`)                                                 |
| `keep_exif`   	| `1` or `0` (default: `0`)                                                 |
| `max_height`   	| `0` or `N` (default: `0` - disabled)                                      |
| `max_width`   	| `0` or `N` (default: `0` - disabled)                                      |
| `url`         	| Required if `type` is `url`                                               |
| `urlN`        	| Required if `type` is `urls`. Can be `url1`,`url2` up to 5.               |
| `file`        	| Required if `type` is `file`                                              |
| `fileN`       	| Required if `type` is `files`. Can be `file1`,`file2` up to 5.            |
| `callback_url`    | If specified the request results will be send to this url using HTTP POST |

**NOTE:** If `max_height` and `max_width` are specified the image will be resized to the bigger one of them keeping the ratio.

## Lossy Optimization
When you decide to sacrifice just a small amount of image quality (usually unnoticeable to the human eye), you will be able to save up to 90% of the initial file weight. Lossy optimization will give you outstanding results with just a fraction of image quality loss.

## Optimization / Fetching results

MegaOptim gives you with two ways to obtain the results of the optimization as follows: 
* Call `https://api.megaoptim.com/optimize/{process_id}/result?timeout=300` endpoint and wait for the result for the specified timeout.
* Provide `callback_url` parameter in your initial request and our servers will send the response to the callback by using HTTP POST.


### 1.) Using /result endpoint

In the following example `65bfc090-a2fc-11e8-ab19-ad2bb706c7e4` is unique `process_id` returned in the initial call. Using it you can query the results. Note that the `process_id` is `unique` for every request you send.

##### Request

Method `POST`, URL: `https://api.megaoptim.com/v1/optimize`

```
{
    type: 'url',
    url: 'https://someurl.com/1.jpg',
    compression: 'intelligent'
}
```

##### Response

```json
{
    "status": "processing",
    "code": 202,
    "process_id": "65bfc090-a2fc-11e8-ab19-ad2bb706c7e4"
}
```

So now we have the `process_id`. We are one step closer to the results and you should send another request to obtain the result as follows:

##### Request

Method `POST`, URL: `https://api.megaoptim.com/v1/optimize/65bfc090-a2fc-11e8-ab19-ad2bb706c7e4/result?timeout=300`

##### Response

```json
{
    "status": "ok",
    "code": 200,
    "result": [
        {
            "file_name": "1.jpg",
            "original_size": 315615,
            "optimized_size": 127380,
            "saved_bytes": 188235,
            "saved_percent": 60,
            "url": "https://srv1.megaoptim.test/b12020cdf3a1/xmdobhRRl7tk6xd.png",
            "success": 1
        }
    ],
    "user": {
        "name": "John Doe",
        "email": "john@doe.com",
        "tokens": 474
    }
}
```


The `timeout` property is used to specify how much seconds to wait for the job to finish. Assuming that we specified `timeout` to be `120`, if the job finishes in less than `120` seconds then it will return the results of the job, otherwise the `status` of the response will stil be `processing`.


### 2.) Fetch: Using `callback_url` parameter

To receive the results using `callback_url` you should provide it in the initial `POST` call. Specify the `callback_url` with your url. Make sure you have the callback method implemented otherwise you will not be able to receive/process the results.

##### Request

Method `POST`, URL: `https://api.megaoptim.com/v1/optimize`

```
{
    type: 'url',
    url: 'https://someurl.com/1.jpg',
    compression: 'intelligent',
    callback_url: 'https://my-awesome-website.com/megaoptim_callback'
}
```

##### Response

```json
{
    "status": "processing",
    "code": 202,
    "process_id": "65bfc090-a2fc-11e8-ab19-ad2bb706c7e4"
}
```

##### Results posted to the Callback URL

```json
{
    "status": "ok",
    "code": 200,
    "id": "65bfc090-a2fc-11e8-ab19-ad2bb706c7e4",
    "result": [
        {
            "file_name": "1.jpg",
            "original_size": 315615,
            "optimized_size": 127380,
            "saved_bytes": 188235,
            "saved_percent": 60,
            "url": "https://srv1.megaoptim.test/b12020cdf3a1/xmdobhRRl7tk6xd.png",
            "success": 1
        }
    ],
    "user": {
        "name": "John Doe",
        "email": "john@doe.com",
        "tokens": 474
    }
}
```

**NOTE:** The `callback_url` must be `public` and accessible by our servers. If by any reason our server fail to access it you can always query the result with using the `/result` endpoint described above.

## Usage

This library provides easy to use interface to utilize the MegaOptim API. In the following example we import megaoptim, make instance of the `Client` and then we call the `optimize` method.

The `optimize` method accepts 3 parameters and all are mandatory
* `resource` (`string`|`tuple`) - This can be local path or `tuple` that contains local paths, or url or `tuple` that contains urls. The `tuple` can be max up to 5 urls/paths.
* `params` (`dict`) - This object contains the API parameters in key:value based representation.
* `timeout` (`integer`) - This is the timeout to wait once the api request is sent. By default it is ignored if you provide `callback_url` in the `params`


**NOTE:** If you provide multiple images as `tuple` they either need to be all local paths or public urls. You can not mix those!

```python
# coding=utf-8

import os

from megaoptim.client.client import Client

# Init MegaOptim API client
api = Client("_YOUR_API_KEY_")
try:
    # This can be url string, url path, tuple of paths (up to 5), tuple of urls (up to 5)
    sources = (
        os.path.dirname(os.path.abspath(__file__)) + os.sep + 'images' + os.sep + '1.png',
        os.path.dirname(os.path.abspath(__file__)) + os.sep + 'images' + os.sep + '2.png',
    )
    # Init empty params, will default to keep_exif=1, cmyktorgb=1, compression=intelligent, max_height=0, max_width=0
    # You can specify your own in params too!
    params = dict()
    # When files are send for processing we are calling another endpoint to get the results.
    # This is timeout for that endpoint. If not results are available in the given
    # seconds then the request will be dropped.
    timeout = 300
    # Optimize the file
    r = api.optimize(sources, params, timeout)
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
```

Depending on a choosen response option (Call /result endpoint or Callback URL) in the data object you will find either the optimization ID or optimization results containing a status property, file name, original file size, optimized file size, amount of savings and array of objects that contain optimized image URL:

```json
{
    "status": "ok",
    "code": 200,
    "result": [
        {
            "file_name": "1.png",
            "original_size": 315615,
            "optimized_size": 127380,
            "saved_bytes": 188235,
            "saved_percent": 60,
            "url": "https://srv1.megaoptim.test/b12020cdf3a1/xmdobhRRl7tk6xd.png",
            "success": 1
        },
        {
            "file_name": "2.png",
            "original_size": 3257509,
            "optimized_size": 1123807,
            "saved_bytes": 2133702,
            "saved_percent": 66,
            "url": "https://srv1.megaoptim.test/b12020cdf3a1/EYLp7KxBfgGt0Ly.png",
            "success": 1
        }
    ],
    "user": {
        "name": "John Doe",
        "email": "john@doe.com",
        "tokens": 1234
    }
}
```
For more examples please see the `examples/` directory.

## Contribution

Feel free to open pull request if you noticed any bug o want to propose improvement.

## Support

If you have any questions feel free to contact us at `support@megaoptim.com`

## License

```
Copyright (c) 2018 IDEOLOGIX MEDIA (https://ideologix.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

See LICENSE.txt for more information.
```