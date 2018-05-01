import os
import sys
from sys import argv
from os.path import exists
import re
import time
import pdb

filename="JMSFS.yml"
Taskmode=""
tasklist=[]
WAITINGFORVALUE="NO"

try:
        connect(userConfigFile='/home/weblogic/weblogic-WebLogicConfig.properties', userKeyFile='/home/weblogic/weblogic-WebLogicKey.properties', url='t3://ulwlspega01:7001',adminServerName='AdminServer')
        edit()
        startEdit()
        # Class Declaration
        class task(list):
            def __init__(self, name):
                self.name=name

            def add_taskproperties(self, key, value):
                self.__dict__[key] = value

            def getname(self):
                return self.name


        taskobj=task('dummy')

        if exists(filename):
            fo=open(filename, 'r+')
            filecontent=fo.readlines()
            for i, line in enumerate(filecontent):
                if "-" in line and not "---" in line:
                    #print "Processing Line",line
                    #NewTask
                    TaskName=line.split("-")[1].split(':')[1].strip()
                    #print "TaskName",TaskName
                    Taskmode='true'
                    if TaskName and Taskmode:
                        #print "IN IF"
                        FSName=line.split(":")[1].strip()

                        # if its dummy Object do not do anything else execute the tasks
                        if not taskobj.name == "dummy":
                            #print taskobj.name, "-->", taskobj.__dict__
                            tasklist.append(taskobj.__dict__)

                        #Create Object with FSName
                        taskobj = task(TaskName)
                        #Set Taskmode off
                        Taskmode='false'

                elif Taskmode == "false" and line.strip():
                    #print "Procesing Line",line
                    #print "IN ELSE"
                    if ":" in line:
                        key=line.split(":", 1)[0].strip()
                        value=line.split(":", 1)[1].strip()
                        if key == "PROPERTY":
                            PROPKEY=value
                            WAITINGFORVALUE="YES"
                        elif WAITINGFORVALUE == "YES" and key == "VALUE":
                            PROPKEY="PROP_"+PROPKEY
                            taskobj.add_taskproperties(PROPKEY, value)
                            WAITINGFORVALUE="NO"
                        elif WAITINGFORVALUE == "NO":
                            taskobj.add_taskproperties(key,value)

        # Create Foreign Servers
        print "\n---- STARTING THE PROCESS TO CREATE FOREIGN JMS RESOURCES"

        for tas in tasklist:
            task=dict(tas)  # Convert StringMAP tas into DICTIONARY task
            if task.__getitem__('name') == "CREATEFS": #Creating Foreign Servers
                print "\n---- CREATING FOREIGN SERVERS"
                print "------ TARGET JMS MODULENAME :",task.__getitem__("MODULE")
                print "------ FOREIGN SERVERNAME :",task.__getitem__('FSNAME')
                cd('/JMSSystemResources/'+task.__getitem__("MODULE")+'/JMSResource/'+task.__getitem__("MODULE"))
                cmo.createForeignServer(task.__getitem__('FSNAME'))

            elif task.__getitem__('name') == "CREATEFSD": #Creating SubDeployments
                print "\n---- CREATING SUB DEPLOYMENTS"
                print "------ JMS MODULENAME :",task.__getitem__("MODULE")
                print "------ SUBDEPLOYMENTNAME : ",task.__getitem__('FSDNAME')
                print "------ TARGET JMS SERVERNAME :",task.__getitem__('TARGET')
                cd('/JMSSystemResources/'+task.__getitem__("MODULE"))
                cmo.createSubDeployment(task.__getitem__('FSDNAME'))
                cd('/JMSSystemResources/'+task.__getitem__("MODULE")+'/SubDeployments/'+task.__getitem__('FSDNAME'))
                TARGET=task.__getitem__('TARGET')
                set('Targets', jarray.array([ObjectName('com.bea:Name='+TARGET+',Type=JMSServer')], ObjectName))

            elif task.__getitem__('name') == "UPDATEFS": #Creating Foreign Servers
                print "\n---- UPDATING THE CRATED FOREIGNSERVERS WITH NECASSARY PROPERTIES AND ATTRIBUTES"

                print "------ FOREIGN SERVERNAME :",task.__getitem__('FSNAME')
                print "------ JMS MODULENAME :",task.__getitem__("MODULE")
                print "------ SUBDEPLOYMENTNAME :",task.__getitem__('FSDNAME')
                print "------ CONNECTIONURL :",task.__getitem__('CONNECTIONURL')
                print "------ INITIALCONTEXTFACTORY :",task.__getitem__('INITIALCONTEXTFACTORY')


                cd('/JMSSystemResources/'+task.__getitem__("MODULE")+'/JMSResource/'+task.__getitem__("MODULE")+'/ForeignServers/'+task.__getitem__('FSNAME'))
                cmo.setSubDeploymentName(task.__getitem__('FSDNAME'))
                cmo.setConnectionURL(task.__getitem__('CONNECTIONURL'))
                #setEncrypted('JNDIPropertiesCredential', 'JNDIPropertiesCredential_1524661492299', '/opt/weblogic/domains/pega_domain/Script1524661323935Config','/opt/weblogic/domains/pega_domain/Script1524661323935Secret')
                cmo.setJNDIPropertiesCredentialEncrypted(task.__getitem__('PASS'))
                cmo.setInitialContextFactory(task.__getitem__('INITIALCONTEXTFACTORY'))
                cd('/JMSSystemResources/'+task.__getitem__("MODULE")+'/JMSResource/'+task.__getitem__("MODULE")+'/ForeignServers/'+task.__getitem__('FSNAME'))

                for entry in task.keys():
                    if "PROP" in entry:
                        print "\n---- SETTING JNDIPROPERTIES FOR FOREIGNSERVER"
                        PROP=entry.split("PROP_")[1]
                        #print "PROP",PROP
                        #print "entry",entry
                        VALUE=task.__getitem__(entry)
                        #print "value",VALUE
                        print "------ PROPERTY",PROP
                        print "------ VALUE",VALUE
                        cmo.createJNDIProperty(PROP)
                        cd('/JMSSystemResources/'+task.__getitem__("MODULE")+'/JMSResource/'+task.__getitem__("MODULE")+'/ForeignServers/'+task.__getitem__('FSNAME')+'/JNDIProperties/'+PROP)
                        cmo.setValue(VALUE)
                        cd('/JMSSystemResources/'+task.__getitem__("MODULE")+'/JMSResource/'+task.__getitem__("MODULE")+'/ForeignServers/'+task.__getitem__('FSNAME'))

            elif task.__getitem__('name') == "CREATEFDEST":  # Creating DESTINATIONS
                print "\n---- CREATING DESTINATIONS AND MAPPING THEM TO FOREIGN SERVERS"
                MODULE=task.__getitem__('MODULE')
                DESTNAME=task.__getitem__('DESTNAME')
                TARGET=task.__getitem__('TARGET')
                LOCALJNDI=task.__getitem__('SETLOCALJNDI')
                REMOTEJNDI=task.__getitem__('SETREMOTEJNDI')
                print "------ JMS MODULE-->",MODULE
                print "------ DESTINATION NAME-->",DESTNAME
                print "------ TARGET SERVER-->",TARGET
                print "------ LOCAL JNDI NAME-->",LOCALJNDI
                print "------ REMOTE JNDI NAME-->",REMOTEJNDI
                cd('/JMSSystemResources/'+MODULE+'/JMSResource/'+MODULE+'/ForeignServers/'+TARGET)
                cmo.createForeignDestination(DESTNAME)
                cd('/JMSSystemResources/'+task.__getitem__("MODULE")+'/JMSResource/'+task.__getitem__("MODULE")+ '/ForeignServers/'+TARGET+'/ForeignDestinations/'+DESTNAME)
                cmo.setLocalJNDIName(LOCALJNDI)
                cmo.setRemoteJNDIName(REMOTEJNDI)

        save()
        activate()

except Exception, err:
        print "---- ERROR: Exception Occured While Executing the Script"
        print "\n---- STACK TRACE\n ",err
        print "\n---- INFO: Cancelling the Edit Session before closing"
        dumpStack()
        cancelEdit('y')
