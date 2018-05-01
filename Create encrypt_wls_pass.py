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
