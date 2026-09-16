import ctypes

_ctuix = ctypes.CDLL("/usr/local/lib/libctuix.dylib")

_ctuix.ctuix_core_init.argtypes = []
_ctuix.ctuix_core_init.restype = None

_ctuix.ctuix_parse.argtypes = [ctypes.c_char_p]
_ctuix.ctuix_parse.restype = ctypes.c_void_p

_ctuix.ctuix_core_run.argtypes = [ctypes.c_void_p]
_ctuix.ctuix_core_run.restype = ctypes.c_int

_ctuix.ctuix_core_end.argtypes = []
_ctuix.ctuix_core_end.restype = None

_ctuix.ctuix_delete.argtypes = [ctypes.c_void_p]
_ctuix.ctuix_delete.restype = None

_ctuix.ctuix_cleanup.argtypes = []
_ctuix.ctuix_cleanup.restype = None

_ctuix.ctuix_error_show.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
_ctuix.ctuix_error_show.restype = None


def init():
    _ctuix.ctuix_core_init()


def parse(path):
    return _ctuix.ctuix_parse(path.encode())


def run(manager):
    return _ctuix.ctuix_core_run(manager)


def delete(manager):
    _ctuix.ctuix_delete(manager)


def end():
    _ctuix.ctuix_core_end()


def cleanup():
    _ctuix.ctuix_cleanup()


def error(title, message):
    _ctuix.ctuix_error_show(title.encode(), message.encode())