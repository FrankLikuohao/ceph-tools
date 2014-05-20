import settings
import subprocess
import time
import os
import errno

def pdsh(nodes, command):
    args = ['pdsh', '-R', 'ssh', '-w', nodes, command]
    print('pdsh: %s' % args)
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  close_fds=True)

def pdcp(nodes, flags, localfile, remotefile):
    args = ['pdcp', '-R', 'ssh', '-w', nodes, localfile, remotefile]
    if flags:
        args = ['pdcp', '-R', 'ssh', '-w', nodes, flags, localfile, remotefile]
    print('pdcp: %s' % args)
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  close_fds=True)

def rpdcp(nodes, flags, remotefile, localfile):
    args = ['rpdcp', '-R', 'ssh', '-w', nodes, remotefile, localfile]
    if flags:
        args = ['rpdcp', '-R', 'ssh', '-w', nodes, flags, remotefile, localfile]
    print('rpdcp: %s'  % args)
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  close_fds=True)

def scp(node, localfile, remotefile):
    args = ['scp', localfile, '%s:%s' % (node, remotefile)]
    print('scp: %s' % args)
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  close_fds=True)

def rscp(node, remotefile, localfile):
    args = ['scp', '%s:%s' % (node, remotefile), localfile]
    print('rscp: %s' % args)
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def make_remote_dir(remote_dir):
    print 'Making remote directory: %s' % remote_dir
    nodes = settings.getnodes('clients', 'osds', 'mons', 'rgws', 'mds')
    pdsh(nodes, 'mkdir -p -m0755 -- %s' % remote_dir).communicate()

def sync_files(remote_dir, local_dir):
    nodes = settings.getnodes('clients', 'osds', 'mons', 'rgws', 'mds')

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    pdsh(nodes, 'sudo chown -R %s.%s %s' % (settings.cluster.get('user'), settings.cluster.get('user'), remote_dir))
    rpdcp(nodes, '-r', remote_dir, local_dir).communicate()

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def setup_valgrind(mode, name, tmp_dir):
    valdir = '%s/valgrind' % tmp_dir
    logfile = '%s/%s.log' % (valdir, name)

    pdsh(settings.getnodes('clients', 'osds', 'mons', 'rgws', 'mds'), 'mkdir -p -m0755 -- %s' % valdir).communicate()
    if mode == 'massif':
        outfile = '%s/%s.massif.out' % (valdir, name)
        return 'valgrind --tool=massif --soname-synonyms=somalloc=*tcmalloc* --massif-out-file=%s --log-file=%s ' % (outfile, logfile)
    if mode == 'memcheck':
        return 'valgrind --tool=memcheck --soname-synonyms=somalloc=*tcmalloc* --log-file=%s ' % (logfile)

    print 'valgrind mode: %s is not supported.' % mode
    return ''
