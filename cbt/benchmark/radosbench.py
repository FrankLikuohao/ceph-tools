import subprocess
import common
import settings
import monitoring

from benchmark import Benchmark

class Radosbench(Benchmark):

    def __init__(self, config):
        super(Radosbench, self).__init__(config)
        self.time =  str(config.get('time', '300'))
        self.concurrent_procs = config.get('concurrent_procs', 1)
        self.concurrent_ops = config.get('concurrent_ops', 16)
        self.write_only = config.get('write_only', False)
        self.op_size = config.get('op_size', 4194304)
        self.pgs_per_pool = config.get('pgs_per_pool', 2048)
        self.run_dir = '%s/radosbench/op_size-%08d/concurrent_ops-%08d' % (self.tmp_dir, int(self.op_size), int(self.concurrent_ops))
        self.out_dir = '%s/radosbench/op_size-%08d/concurrent_ops-%08d' % (self.archive_dir, int(self.op_size), int(self.concurrent_ops))

    def initialize(self): 
        super(Radosbench, self).initialize()
        if settings.cluster.get('rebuild_every_test', False):
            # Setup the pools
            for i in xrange(self.concurrent_procs):
                common.pdsh(settings.cluster.get('head'), 'sudo ceph osd pool create rados-bench-%s %d %d' % (i, self.pgs_per_pool, self.pgs_per_pool)).communicate()
                common.pdsh(settings.cluster.get('head'), 'sudo ceph osd pool set rados-bench-%s size 1' % i).communicate()

        # Create the run directory
        common.make_remote_dir(self.run_dir)

        # Check the health before we start the benchmarks
        print 'Checking Health.'
        common.check_health()


    def run(self):
        super(Radosbench, self).run()

#        common.make_remote_dir('%s/write' % self.run_dir)
#        monitoring.start('%s/write' % self.run_dir)
#        # Run rados bench
#        print 'Running radosbench write test.'
#        ps = []
#        for i in xrange(self.concurrent_procs):
#            out_file = '%s/write/output.%s' % (self.run_dir, i)
#            objecter_log = '%s/write/objecter.%s.log' % (self.run_dir, i)
#            p = common.pdsh(settings.cluster.get('clients'), '/usr/bin/rados -p rados-bench-%s %s bench %s write %s --no-cleanup 2> %s > %s' % (i, op_size_str, self.time, concurrent_ops_str, objecter_log, out_file))
#            ps.append(p)
#        for p in ps:
#            print p.wait()
#        monitoring.stop('%s/write' % self.run_dir)
#        common.sync_files('%s/write/*' % self.run_dir, '%s/write' % self.out_dir)
        # Run write test
        self._run('write', '%s/write' % self.run_dir, '%s/write' % self.out_dir)
        # Run read test unless write_only 
        if self.write_only: return
        self.dropcaches()
        self._run('seq', '%s/seq' % self.run_dir, '%s/seq' % self.out_dir)
#        common.make_remote_dir('%s/seq' % self.run_dir)
#        monitoring.start('%s/seq' % self.run_dir)
#        # Run rados bench
#        print 'Running radosbench read test.'
#        ps = []
#        for i in xrange(self.concurrent_procs):
#            out_file = '%s/seq/output.%s' % (self.run_dir, i)
#            objecter_log = '%s/seq/objecter.%s.log' % (self.run_dir, i)
#            p = common.pdsh(settings.cluster.get('clients'), '/usr/bin/rados -p rados-bench-%s %s bench %s seq %s --no-cleanup 2> %s > %s' % (i, op_size_str, self.time, concurrent_ops_str, objecter_log, out_file))
#            ps.append(p)
#        for p in ps:
#            p.wait()
#        monitoring.stop('%s/seq' % self.run_dir)
#        common.sync_files('%s/seq/*' % self.run_dir, '%s/seq' self.out_dir)

    def _run(self, mode, run_dir, out_dir):
        # We'll always drop caches for rados bench
        self.dropcaches()

        if self.concurrent_ops:
            concurrent_ops_str = '--concurrent-ios %s' % self.concurrent_ops
        op_size_str = '-b %s' % self.op_size

        common.make_remote_dir(run_dir)
        monitoring.start(run_dir)
        # Run rados bench
        print 'Running radosbench read test.'
        ps = []
        for i in xrange(self.concurrent_procs):
            out_file = '%s/output.%s' % (run_dir, i)
            objecter_log = '%s/objecter.%s.log' % (run_dir, i)
            p = common.pdsh(settings.cluster.get('clients'), '/usr/bin/rados -p rados-bench-%s %s bench %s %s %s --no-cleanup 2> %s > %s' % (i, op_size_str, self.time, mode, concurrent_ops_str, objecter_log, out_file))
            ps.append(p)
        for p in ps:
            p.wait()
        monitoring.stop(run_dir)
        common.sync_files('%s/*' % run_dir, out_dir)


#    def cleanup(self):
#        common.sync_files('%s/*' % self.run_dir, self.out_dir)

    def __str__(self):
        return "%s\n%s\n%s" % (self.run_dir, self.out_dir, super(Radosbench, self).__str__())
