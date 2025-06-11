from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class FileProcessingAnonThrottle(AnonRateThrottle):
    scope = 'file_processing_anon'
    

class FileProcessingUserThrottle(UserRateThrottle):
    scope = 'file_processing_user'
