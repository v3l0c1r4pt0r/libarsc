## \file exceptions.py
#  \brief libarsc exceptions

class WrongTypeException(Exception):

    def __init__(self, field, headerType):
        super().__init__(self, '{} must be of type {}'.format(field,
            headerType.__name__))

class ChunkHeaderWrongTypeException(Exception):

    def __init__(self, expectedType, chunkType=None):
        super().__init__(self, 'header must describe resource of type ' \
                '{expects}{got}'.format(expects=expectedType.name,
                    got=' (got {})'.format(chunkType.name) if \
                    chunkType else ''))
