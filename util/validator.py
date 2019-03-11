from lib.target import Target


def validateTarget(host):
    target = Target(host)
    if not target.isValid():
        return False
    return target
