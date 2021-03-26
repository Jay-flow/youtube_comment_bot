class NoPopupError(Exception):
    def __init__(self, message="팝업을 찾을 수가 없습니다."):
        super().__init__(message)


