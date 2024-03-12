from enum import Enum

class FreqEnum(Enum):
    SECONDLY = 's'
    MINUTELY = 't'
    HOURLY = 'h'
    DAILY = 'd'
    BUSINESS = 'b'
    WEEKLY = 'w'
    MONTHLY = 'm'

class ExceptionEnum(Enum):
    DEFAULT_EXCEPTION = 'An error occured in the backend'
    FAILED_UPLOAD = 'Failed to upload document'
    EXTENSION_NOT_ALLOWED = 'Only csv and xlsx files are allowed'
    FAILED_CREATE_SESSION_ID = 'Failed to create session id'
    FAILED_CREATE_SESSION_DIR = 'Failed to create session directory'
    FAILED_CREATE_SESSION = 'Failed to create session'