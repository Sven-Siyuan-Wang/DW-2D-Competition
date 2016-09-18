import urllib2
tasks={}
for line in urllib2.urlopen("http://people.sutd.edu.sg/~oka_kurniawan/10_009/y2015/2d/tests/level2_2.inp"):
        tasks[line.split()[0]]=int(line.split()[1])
bot1=[]
bot2=[]
for site in tasks:
    if tasks[site]>=6:
        count=tasks[site]/6
        if site in 'CD':
            bot1.extend([site]*count)
        elif site in 'AB':
            bot2.extend([site]*count)
        else:
            print 'Destination name illegal'
        tasks[site]/=6
for site in ['A','B','C','D']
print bot1,bot2