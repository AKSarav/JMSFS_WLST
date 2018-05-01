# JMSFS_WLST
This is created in python and should be invoked with WLST for creating the Foreign Servers, Foreign Server Subdeployments, Foreign Server Destinations under the specified JMS Module


# How it is setup 
The Script is designed in python(jython) to run in WLST scripting mode. It reads the configuration data inputs from a YAML file named JMSFS.yml. This Yml file name must not be changed unless you are updating the filename in the PYTHON script as well.

# First things First
1)  The order of the tasks in YAML file is important and should not be broken. As the script reads and execute the tasks as the order it was mentioned in the YAML file

2)  The input properties file have been created in YAML KEY:VALUE combination  for better understanding and readability.Please be informed that the input yaml file is not using the Complete YAML syntax. ( its a just another property file created in YAML, Thats it :) )

3)  You can add more JNDI properties (or) remove the unwanted property from the YAML file but make sure you remove both PROPERTY and VALUE attributes and vice versa

```
PROPERTY: java.naming.security.principal
      VALUE: username  
```

4) Except `PROPERTY` and `VALUE` all other Attributes(Keys) and Values are mandatory for a TASK

5) Input YAML file is using basic `key:value` syntax and `value` field should not contain `"` double/single quotes

```
# CORRECT

FSNAME: ForeignServer1
FSDNAME: ForeignServer1SD

# INCORRECT

FSNAME: "ForeignServer1"
FSDNAME: "ForeignServer1SD"


```
6) This is a minimal set of configuration,  the YAML file could have in the expected order of tasks

```yaml
---

- TASKNAME: CREATEFS
  FSNAME: ForeignServer1  
  MODULE: jmsmodule1 


- TASKNAME: CREATEFSD
  FSDNAME: ForeignServer1SD  
  MODULE: jmsmodule1 
  TARGET: jmsserver1


- TASKNAME: UPDATEFS
    FSNAME: ForeignServer1
    FSDNAME: ForeignServer1SD
    MODULE: jmsmodule1
    SUBDEPLOYMENTNAME: ForeignServer1SD
    CONNECTIONURL: tcp://sonicmq-node1:2506,tcp://sonicmq-node2:2506
    PASS: <Encrypted Password String>
    INITIALCONTEXTFACTORY: com.sonicsw.jndi.mfcontext.MFContextFactory
    PROPERTY: com.sonicsw.jndi.mfcontext.idleTimeout
      VALUE: 6000 
    PROPERTY: com.sonicsw.jndi.mfcontext.domain
      VALUE: JMS_UAT
    PROPERTY: java.naming.security.principal
      VALUE: username 
    

#Create new destination
- TASKNAME: CREATEFDEST
  DESTNAME: sometopic
  TARGET: ForeignServer1
  MODULE: jmsmodule1
  SETLOCALJNDI: jms/sometopic
  SETREMOTEJNDI: SonicJMS.Topic.SOMETOPIC

- TASKNAME: END # This was created just to tell the script to STOP processing 

```

7) We presume that you have created JMSServer already and the JMSServer name you are mentioning the YAML file is available in the weblogic domain

8) **DO NOT FORGET** to update the values in YAML file according to your requirement before executing it *Except the Value of TASKNAME key*

9) **SUPPLY ONLY ENCRYPTED PASSWORD** in yaml file. You have to use corresponding weblogic server's commandline to encrypt the password

You can also use the following shell script to securely encrypt any password for weblogic. All you have to do is passing the domain/bin directory location


**Script**
```shell
#!/bin/bash
echo -e "Enter the Domain/bin Directory Location"
read domaindir
if [ ! -d $domaindir ]
then
        echo -e "Directory not exists"
else
        cd $domaindir
        echo -e "Trying to find the SetDomainEnv.sh file \n"
        if [ ! -f setDomainEnv.sh ]
        then
                echo -e "Unable to find the SetDomainEnv.sh file"
        else
                echo -e "Executing  SetDomainEnv"
                . ./setDomainEnv.sh
                tc=`java weblogic.security.Encrypt test 2>/dev/null|wc -l`
                if [ $tc -ne 0 ]
                then
                        echo -e "Enter the Password to encrypt"
                        read -s pass
                        echo -e "Encrypted Password is"
                        java weblogic.security.Encrypt $pass
                fi
        fi
fi


```
**Sample Execution** 
```shell

weblogic@mwinventory.in> ./encrypt_wls_pass.py
Enter the Domain/bin Directory Location
/opt/weblogic/domains/mwi_domain/bin
Trying to find the SetDomainEnv.sh file

Executing  SetDomainEnv
Enter the Password to encrypt
Encrypted Password is
{AES}YQa2Qwh2IyjJXKPdG1IcTCHUZ5NuN46vfaJaydVwli4=
```


## How to Execute the script
1) Place the input YAML file **JMSFS.yml** and the **JMSFS_Setup.py** script in the same directory
2) Execute *SetDomainEnv.sh (or) SetWLSEnv.sh* to set the WLST environment ( Or if you have did the previous step to encrypt the password then you can skip this)
3) Invoke WLST and pass this python script as argument as shown below

```java weblogic.WLST JMSFS_Setup.py```


## Sample Execution Log

```yaml
weblogic@mwinventory.in> java weblogic.WLST JMSFS_WLST.py

Initializing WebLogic Scripting Tool (WLST) ...

Welcome to WebLogic Server Administration Scripting Shell

Type help() for help on available commands

Connecting to t3://wls.mwinventory.in:7001 with userid weblogic ...
Successfully connected to Admin Server "AdminServer" that belongs to domain "mwi_domain".

Warning: An insecure protocol was used to connect to the
server. To ensure on-the-wire security, the SSL port or
Admin port should be used instead.

Location changed to edit tree. This is a writable tree with
DomainMBean as the root. To make changes you will need to start
an edit session via startEdit().

For more help, use help('edit')

Starting an edit session ...
Started edit session, please be sure to save and activate your
changes once you are done.

---- STARTING THE PROCESS TO CREATE FOREIGN JMS RESOURCES

---- CREATING FOREIGN SERVERS
------ TARGET JMS MODULENAME : JMSModule1
------ FOREIGN SERVERNAME : ForeignServer1

---- CREATING FOREIGN SERVERS
------ TARGET JMS MODULENAME : JMSModule1
------ FOREIGN SERVERNAME : ForeignServer2

---- CREATING SUB DEPLOYMENTS
------ JMS MODULENAME : JMSModule1
------ SUBDEPLOYMENTNAME :  ForeignServer1SD
------ TARGET JMS SERVERNAME : PRJMS_Server1

---- CREATING SUB DEPLOYMENTS
------ JMS MODULENAME : JMSModule1
------ SUBDEPLOYMENTNAME :  ForeignServer2SD
------ TARGET JMS SERVERNAME : PRJMS_Server2

---- UPDATING THE CRATED FOREIGNSERVERS WITH NECASSARY PROPERTIES AND ATTRIBUTES
------ FOREIGN SERVERNAME : ForeignServer1
------ JMS MODULENAME : JMSModule1
------ SUBDEPLOYMENTNAME : ForeignServer1SD
------ CONNECTIONURL : tcp://sonicmq-node1:2506,tcp://sonicmq-node2:2506
------ INITIALCONTEXTFACTORY : com.sonicsw.jndi.mfcontext.MFContextFactory

---- SETTING JNDIPROPERTIES FOR FOREIGNSERVER
------ PROPERTY java.naming.security.principal
------ VALUE dummyuser

---- SETTING JNDIPROPERTIES FOR FOREIGNSERVER
------ PROPERTY com.sonicsw.jndi.mfcontext.idleTimeout
------ VALUE 6000

---- SETTING JNDIPROPERTIES FOR FOREIGNSERVER
------ PROPERTY com.sonicsw.jndi.mfcontext.domain
------ VALUE JMS_UAT

---- UPDATING THE CRATED FOREIGNSERVERS WITH NECASSARY PROPERTIES AND ATTRIBUTES
------ FOREIGN SERVERNAME : ForeignServer2
------ JMS MODULENAME : JMSModule1
------ SUBDEPLOYMENTNAME : ForeignServer2SD
------ CONNECTIONURL : tcp://sonicmq-node1:2506,tcp://sonicmq-node2:2506
------ INITIALCONTEXTFACTORY : com.sonicsw.jndi.mfcontext.MFContextFactory

---- SETTING JNDIPROPERTIES FOR FOREIGNSERVER
------ PROPERTY java.naming.security.principal
------ VALUE dummyuser

---- SETTING JNDIPROPERTIES FOR FOREIGNSERVER
------ PROPERTY com.sonicsw.jndi.mfcontext.idleTimeout
------ VALUE 6000

---- SETTING JNDIPROPERTIES FOR FOREIGNSERVER
------ PROPERTY com.sonicsw.jndi.mfcontext.domain
------ VALUE JMS_UAT

---- CREATING DESTINATIONS AND MAPPING THEM TO FOREIGN SERVERS
------ JMS MODULE--> JMSModule1
------ DESTINATION NAME--> CheckPrinted
------ TARGET SERVER--> ForeignServer1
------ LOCAL JNDI NAME--> jms/TestTopic
------ REMOTE JNDI NAME--> SonicJMS.Topic.TestTopic

---- CREATING DESTINATIONS AND MAPPING THEM TO FOREIGN SERVERS
------ JMS MODULE--> JMSModule1
------ DESTINATION NAME--> OFACExternalSourceStatusChangeSub
------ TARGET SERVER--> ForeignServer1
------ LOCAL JNDI NAME--> jms/mwiTopic
------ REMOTE JNDI NAME--> SonicJms.Topic.mwiTopic

---- CREATING DESTINATIONS AND MAPPING THEM TO FOREIGN SERVERS
------ JMS MODULE--> JMSModule1
------ DESTINATION NAME--> CheckPrinted
------ TARGET SERVER--> ForeignServer2
------ LOCAL JNDI NAME--> jms/TestTopic
------ REMOTE JNDI NAME--> SonicJMS.Topic.TestTopic

---- CREATING DESTINATIONS AND MAPPING THEM TO FOREIGN SERVERS
------ JMS MODULE--> JMSModule1
------ DESTINATION NAME--> OFACExternalSourceStatusChangeSub
------ TARGET SERVER--> ForeignServer2
------ LOCAL JNDI NAME--> jms/mwiTopic
------ REMOTE JNDI NAME--> SonicJms.Topic.mwiTopic
Saving all your changes ...
Saved all your changes successfully.
Activating all your changes, this may take a while ...
The edit lock associated with this edit session is released
once the activation is completed.
Activation completed

```

## End Note
You can fork it, modify it, tweak it to suit your needs. For any feedback or help write to me at aksarav@mwinventory.in.



