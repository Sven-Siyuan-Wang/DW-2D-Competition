

    

tasks={'A':3,'B':13,'C':7,'D':3} 
#for line in urllib2.urlopen("http://people.sutd.edu.sg/~oka_kurniawan/10_009/y2015/2d/tests/level2_1.inp"):
#        tasks[line.split()[0]]=int(line.split()[1])
bot=[]
leftover=''
l=['A','B','C','D']
for site in l:
    if tasks[site]>=6:
        count=tasks[site]/6
        bot.extend([site]*count)        
        tasks[site]%=6
    
sum4=0
done=False

#print tasks
#FOUR
for a in tasks.values():
    if a==0:
        sum4=10
        break
    else:
        sum4+=a
if sum4<=6:
    leftover='ABCD'
    bot.append(leftover)
    for i in l:
        tasks[i]=0
    done=True

#print 'after 4 check',tasks
#Check for 'AB','CD' case
if not done and [tasks[i]>0 for i in l]:   #tasks['A']>0 and tasks['B']>0 and tasks['C']>0 and tasks['D']>0:
    if tasks['A']+tasks['B']<=6 and tasks['C']+tasks['D']<=6:
        bot.append('AB')
        bot.append('CD')
        done=True
        for i in l:
            tasks[i]=0 
    

#THREE destinations 
done3=False
if not done:
    cases=['ABC','ABD','ACD','BCD']
    for i in cases:
        sum3=0
        for j in i:
            if tasks[j]==0:
                sum3=10
                
            else:
                sum3+=tasks[j]
        if sum3<=6:
            print 'sum3<=6'
            leftover+=i
            bot.append(leftover)
            leftover=''
            done3=True
            for j in i:
                tasks[j]=0
            break
#print 'after 3 check',tasks

#Check for double destinations
if not done3 and not done:
    for i in range(3):
        if tasks[l[i]]>0:
            for j in range (i+1,4):
                if tasks[l[i]]+tasks[l[j]]<=6 and tasks[l[j]]>0 and tasks[l[i]]>0:
                    leftover=l[i]+l[j]
                    print leftover
                    bot.append(leftover)
                    tasks[l[i]]=0
                    tasks[l[j]]=0
# Check for single desitinations left
if not done:
    for i in l:
        if tasks[i]>0:
            bot.append(i)
            tasks[i]=0
print tasks
order='X'.join(bot)
order=list(order+'X')
    
print bot,order