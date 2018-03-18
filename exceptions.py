## \file exceptions.py
#  \brief libarsc exceptions

class WrongTypeException(Exception):

    def __init__(self, field, headerType):
        super().__init__(self, '{} must be of type {}'.format(field,
            headerType.__name__))

class ChunkHeaderWrongTypeException(Exception):

    def __init__(self, chunkType):
        super().__init__(self, 'header must describe resource of type ' \
                '{}'.format(chunkType.name))
