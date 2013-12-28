import subprocess

import settings
import common
import monitoring

from cluster.ceph import Ceph

class Benchmark(object):
    def __init__(self, config):
        self.config = config
        self.cluster = Ceph(settings.cluster)
        self.archive_dir = "%s/%08d" % (settings.cluster.get('archive_dir'), config.get('iteration'))
        self.osd_ra = config.get('osd_ra', 128)

    def getclass(self):
        return self.__class__.__name__

    def initialize(self):
        pass

    def run(self):
        print "Setting OSD Read Ahead to: %s" % self.osd_ra
        self.cluster.set_osd_param('read_ahead_kb', self.osd_ra)

    def cleanup(self):
        pass

    def dropcaches(self):
        nodes = settings.getnodes('clients', 'osds') 

        common.pdsh(nodes, 'sync').communicate()
        common.pdsh(nodes, 'echo 3 | sudo tee /proc/sys/vm/drop_caches').communicate()

    def __str__(self):
        return str(self.config)
