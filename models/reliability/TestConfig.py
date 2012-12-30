#!/usr/bin/python
#
# note that by this point, all times are in hours
#

MB = 1000000
GB = MB * 1000
TB = GB * 1000


class TestConfig:

    def __init__(self):
        """ default test parameters """

        self.period = 365.25 * 24

        self.disk_size = 2 * TB

        self.raid_vols = 2
        self.raid_replace = 6
        self.raid_recover = 50 * MB
        self.raid_scrub = False

        self.rados_copies = 2
        self.rados_markout = 10.0 / 60
        self.rados_recover = 50 * MB
        self.rados_decluster = 200
