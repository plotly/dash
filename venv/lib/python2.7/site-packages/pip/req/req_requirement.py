from pip._vendor.packaging.version import parse as parse_version


class InstallationCandidate(object):

    def __init__(self, project, version, location):
        self.project = project
        self.version = parse_version(version)
        self.location = location
        self._key = (self.project, self.version, self.location)

    def __repr__(self):
        return "<InstallationCandidate({0!r}, {1!r}, {2!r})>".format(
            self.project, self.version, self.location,
        )

    def __hash__(self):
        return hash(self._key)

    def __lt__(self, other):

        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s <= o)

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s == o)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s > o)

    def __ne__(self, other):
        return self._compare(other, lambda s, o: s != o)

    def _compare(self, other, method):
        if not isinstance(other, InstallationCandidate):
            return NotImplemented

        return method(self._key, other._key)
