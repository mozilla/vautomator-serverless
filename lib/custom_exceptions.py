from tenable_io.exceptions import TenableIOApiException, TenableIOException


class TenableScanRunningException(TenableIOApiException):
    pass


class TenableScanUnexpectedStateException(TenableIOApiException):
    pass


class TenableScanCompleteException(TenableIOException):
    pass


class PartialScanResultsException(Exception):
    pass


class NoResultsFoundException(Exception):
    pass
