class CSVReaderError(BaseException):
    def __init__(self, message):
        self.message = f'CVSReaderError: {message}'
        super().__init__(message)