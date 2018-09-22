import platform

try:
    from cStringIO import OutputType as cStringIO
except ImportError:
    from io import BytesIO as cStringIO

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def is_windows():
    return platform.system() == 'Windows'


def is_linux():
    return platform.system() == 'Linux'


def is_osx():
    return platform.system() == 'Darwin'


def validate_url(x):
    try:
        result = urlparse(x)
        return result.scheme and result.netloc and result.path
    except:
        return False


def maybe_set_default(key, value, p):
    if key not in p:
        p[key] = value
    return p


def get_file(resource):
    if isinstance(resource, cStringIO):
        _file = resource.getvalue()
    else:
        _file = open(resource, 'rb')
    return _file
