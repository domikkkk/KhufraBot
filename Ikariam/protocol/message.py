import ctypes


class Message(ctypes.Structure):
    bot_type: int
    bot_id: int
    to_bot_type: int
    content: bytes  # lub: str, ale lepiej bytes przy c_char[]

    _fields_ = [
        ("bot_type", ctypes.c_uint8),  # who_type
        ("bot_id", ctypes.c_uint8),  # who_id
        ("to_bot_type", ctypes.c_uint8),  # whom_type
        ("content", ctypes.c_char * 100)  # message
    ]
    
    @classmethod
    def size(cls) -> int:
        return ctypes.sizeof(cls)

    def to_bytes(self) -> bytes:
        return bytes(self)

    @classmethod
    def from_bytes(cls, data: bytes) -> "Message":
        if len(data) < cls.size():
            data = data.ljust(cls.size(), b'\x00') 
        return cls.from_buffer_copy(data)


