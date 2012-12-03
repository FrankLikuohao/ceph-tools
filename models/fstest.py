#!/usr/bin/python
#
# disk simulation exerciser
#   prints out all of the interesting disk performance
#   parameters and simulated bandwidth for standard tests

# mnemonic scale constants
MILLION = 1000000    # capacities and speeds

import SimFS


def kb(val):
    """ number of kilobytes (1024) in a block """
    return val / 1024

def iops(us):
    """ convert a us/operation into IOPS """
    return 1000000 / us


def bw(bs, us):
    """ convert block size and us/operation into MB/s bandwidth """
    return bs / us


def fstest(fs, filesize=16 * MILLION, depth=1, sync=False):
    """ compute & display standard fio to filesystem on a disk """

    print("\t    bs\t    seq read\t   seq write\t   rnd read\t   rnd write")
    print("\t -----\t    --------\t   ---------\t   --------\t   ---------")
    for bs in (4096, 128 * 1024, 4096 * 1024):
        tsr = fs.avgTime(bs, filesize, read=True, seq=True, depth=depth, sync=sync)
        tsw = fs.avgTime(bs, filesize, read=False, seq=True, depth=depth, sync=sync)
        trr = fs.avgTime(bs, filesize, read=True, seq=False, depth=depth, sync=sync)
        trw = fs.avgTime(bs, filesize, read=False, seq=False, depth=depth, sync=sync)

        print("\t%5dK\t %6d MB/s\t %6d MB/s\t %6.1f MB/s\t %6.1f MB/s" % \
                (kb(bs), bw(bs, tsr), bw(bs, tsw), \
                         bw(bs, float(trr)), bw(bs, float(trw))))
        print("\t    \t %6d IOPS\t %6d IOPS\t %6d IOPS\t %6d IOPS" % \
                (iops(tsr), iops(tsw), iops(trr), iops(trw)))
