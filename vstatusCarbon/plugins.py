import os

def get_cpu(host, now):
    #f=open("/tmp/vestat",'r')
    f=open("/proc/vz/vestat",'r')
    ret=[]

    for l in f.readlines():
        x=l.split()
        if x[0].isdigit():
            en=map(int,x)
        else:
            continue
        ret.append("%s.openvz.%d.cpu %d %d" % (host, en[0], en[1]+en[2]+en[3], now))
    f.close()
        
    return ret

def get_ub(host, now):
    params=['privvmpages', 'dcachesize', 'kmemsize', 'physpages', 'numproc', 'numfile']

    f=open("/proc/bc/resources",'r')
    #f=open("/tmp/r",'r')

    ret=[]

    f.readline()
    head=f.readline()

    vps=0

    for l in f.readlines():
        v=l.split()
        if v[0].endswith(':') and v[0][:-1].isdigit():
	    vps=int(v[0][:-1])
            if v[1] in params:
                ret.append('%s.openvz.%d.%s %d %d' % (host, vps, v[1], int(v[2]), now))
	else:
            if v[0] in params:
                ret.append('%s.openvz.%d.%s %d %d' % (host, vps, v[0], int(v[1]), now))
	    
    f.close()
    return ret

def get_io(host,now):
    ret=[]
    f=open('/proc/bc/iostat','r')
    #f=open('/tmp/i','r')

    f.flush()
    ln=map(lambda x: x.split(), f.readlines())
    f.close()

    for l in ln:
	if l[0] in ('flush', 'fuse'):
	    continue

	ret.append('%s.openvz.%d.iops %d %d' % (host, int(l[1]), int(l[8]), now))

    vzlist=os.listdir('/proc/bc')

    for vzid in vzlist:
        if os.path.isdir('/proc/bc/%s' % vzid):
	    f=open('/proc/bc/%d/ioacct' % int(vzid))
	    ioacct=dict(map(lambda x: x.split(), f.readlines()))
	    f.close()
	    ret.append('%s.openvz.%d.io_pbs %d %d' % (host, int(vzid), int(ioacct['io_pbs']), now))
	    ret.append('%s.openvz.%d.read %d %d' % (host, int(vzid), int(ioacct['read']), now))
	    ret.append('%s.openvz.%d.write %d %d' % (host, int(vzid), int(ioacct['write']), now))
	    ret.append('%s.openvz.%d.dirty %d %d' % (host, int(vzid),int(ioacct['dirty'])-int(ioacct['write'])-int(ioacct['cancel'])-int(ioacct['missed']), now))

    return ret

def get_quota(host,now):
    ret=[]
    f=open('/proc/vz/vzquota','r')

    f.readline()

    f.flush()
    ln=map(lambda x: x.split(), f.readlines())
    f.close()

    for l in ln:
        print l
        if l[0].endswith(':'):
            vps=int(l[0][:-1])
            continue
        if l[0] in ('1k-blocks', 'inodes'):
            ret.append('%s.openvz.%d.%s %d %d' % (host, vps, l[0], int(l[1]), now))
    return ret

def get_cgroup(host, now):
    ret=[]
    
    masters=os.listdir('/cgroup/php')

    for m in masters:
        if os.path.isdir('/cgroup/php/%s' % m):
            f=open('/cgroup/php/%s/cpuacct.usage' % m, 'r')
            i=int(f.read())/1000000
            f.close()
            ret.append('%s.cgroup.%s.usage %d %d' % (host, m, i, now))
    return ret

def get_cgroup_io(host, now):
    ret=[]

    f=open('/cgroup/blkio.throttle.io_serviced', 'r')
    for l in f.readlines():
	if l.startswith(config['home_dev']):
    	    c=l.split()
            if c[1] in ('Read', 'Write'):
        	ret.append('%s.cgroup.root.io.root_%s %d %d' % (host, c[1].lower(),int(c[2]), now))
    f.close()

    f=open('/cgroup/blkio.throttle.io_service_bytes', 'r')
    for l in f.readlines():
      if l.startswith(config['home_dev']):
        c=l.split()
        if c[1] in ('Read', 'Write'):
          ret.append('%s.cgroup.root.io.root_%s_bytes %d %d' % (host, c[1].lower(),int(c[2]), now))
    f.close()

    masters=os.listdir('/cgroup/php')

    for m in masters:
        if os.path.isdir('/cgroup/php/%s' % m):
            f=open('/cgroup/php/%s/blkio.throttle.io_serviced' % m, 'r')
            for l in f.readlines():
              if l.startswith(config['home_dev']):
                c=l.split()
                if c[1] in ('Read', 'Write'):
                  ret.append('%s.cgroup.%s.io.%s %d %d' % (host, m, c[1].lower(),int(c[2]), now))
            f.close()

            f=open('/cgroup/php/%s/blkio.throttle.io_service_bytes' % m, 'r')
            for l in f.readlines():
              if l.startswith(config['home_dev']):
                c=l.split()
                if c[1] in ('Read', 'Write'):
                  ret.append('%s.cgroup.%s.io.%s_bytes %d %d' % (host, m, c[1].lower(),int(c[2]), now))
            f.close()

    return ret

mem_stats=['rss', 'cache', 'pgfault','pgmajfault', 'active_file', 'inactive_file']

def get_cgroup_memory(host, now):
    ret=[]
    masters=os.listdir('/cgroup/php')

    for m in masters:
        if os.path.isdir('/cgroup/php/%s' % m):
	    f=open('/cgroup/php/%s/memory.stat' % m, 'r')
	    stats=dict(map(lambda x: x.split(), f.readlines()))
    	    f.close()
	    for i in mem_stats:
    		ret.append('%s.cgroup.%s.memory.%s %d %d' % (host, m, i, int(stats.get(i, '0')), now))

	    f=open('/cgroup/php/%s/memory.usage_in_bytes' % m, 'r')
	    ret.append('%s.cgroup.%s.memory.used %d %d' % (host, m,int(f.read()), now))
	    f.close()

    f=open('/cgroup/php/memory.usage_in_bytes', 'r')
    ret.append('%s.cgroup.root.memory.used %d %d' % (host, int(f.read()), now))
    f.close()
    
    return ret

plugins=[]
config={}


try:
    import MySQLdb
except Exception, e:
    print e

def get_mysql(host, now):
    try:
        ret=[]
        db=MySQLdb.connect(host='127.0.0.1', user=config['mysql_user'], passwd=config['mysql_password'])
        c=db.cursor()
        
        stat={}
        
        c.execute('SHOW user_statistics')
        for l in c.fetchall():
            ret.append('%s.mysql.%s.Total_connections %d %d' % (host, l[0], int(l[1]), now))
            ret.append('%s.mysql.%s.Concurrent_connections %d %d' % (host, l[0], int(l[2]), now))
            ret.append('%s.mysql.%s.Busy_time %d %d' % (host, l[0], int(l[4]), now))
            ret.append('%s.mysql.%s.Bytes_received %d %d' % (host, l[0], int(l[6]), now))
            ret.append('%s.mysql.%s.Bytes_sent %d %d' % (host, l[0], int(l[7]), now))
            ret.append('%s.mysql.%s.Rows_fetched %d %d' % (host, l[0], int(l[9]), now))
            ret.append('%s.mysql.%s.Rows_updated %d %d' % (host, l[0], int(l[10]), now))

    except Exception, e:
	print e

    return ret

if len(plugins) == 0:
  if os.path.exists('/proc/vz/vzquota'):
    plugins.append(get_quota)
  if os.path.exists('/proc/bc/iostat'):
    plugins.append(get_io)
  if os.path.exists("/proc/vz/vestat"):
    plugins.append(get_cpu)
  if os.path.exists("/proc/bc/resources"):
    plugins.append(get_ub)
  if os.path.exists("/cgroup/php/cpuacct.usage"):
    plugins.append(get_cgroup)
  if os.path.exists("/cgroup/php/memory.stat"):
    plugins.append(get_cgroup_memory)
  if os.path.exists("/cgroup/php/blkio.throttle.io_serviced"):
    plugins.append(get_cgroup_io)
    homedev=os.stat('/home/www').st_dev
    config['home_dev']='%d:%d' % (os.major(homedev), os.minor(homedev))

  try:
    import MySQLdb
      
    if os.path.isfile('/root/.my.cnf'):
        f=open('/root/.my.cnf')
        l=f.readlines()
        f.close()
        cfg={}
        for line in l:
            c=line.strip().split('=')
            if len(c) == 2 and not c[0].startswith(';'):
                cfg[c[0]]=c[1]
        if cfg.has_key('user') and cfg.has_key('password'):
            config['mysql_user']=cfg['user']
	    config['mysql_password']=cfg['password']
	    plugins.append(get_mysql)
  except Exception,e:
    print e


if __name__ == '__main__':
    print get_io('test',99)
    #print plugins
    #for p in plugins:
    #  print p('xeon', 999)
