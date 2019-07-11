from lib.custom_exceptions import *


class TestCustomExceptions():

    def test_creation(self):
        ex_1 = TenableScanRunningException()
        ex_2 = TenableScanUnexpectedStateException()
        ex_3 = TenableScanCompleteException()
        ex_4 = TenableScanInterruptedException()

        assert type(ex_1) is TenableScanRunningException
        assert type(ex_2) is TenableScanUnexpectedStateException
        assert type(ex_3) is TenableScanCompleteException
        assert type(ex_4) is TenableScanInterruptedException
