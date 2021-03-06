#!/bin/bash

#Install Informix (https://www.raspberrypi.org/forums/viewtopic.php?t=97199&p=674959)
cd ~

#let's check to make sure the Informix binary is present
if [ -e ~/ids.12.10.UC6DE.Linux-ARM6.tar ]
then 
  mkdir /tmp/ifxinstall
  cd /tmp/ifxinstall
  mv ~/ids.12.10.UC6DE.Linux-ARM6.tar .
  tar xvf /tmp/ifxinstall/ids.12.10.UC6DE.Linux-ARM6.tar

  sudo groupadd informix
  sudo useradd -g informix -m informix
  sudo bash -c "echo informix:informix | chpasswd informix"

  # Make sure to add the user informix to the /etc/sudoers file by adding the following line by using the 'sudo visudo' command:
  sudo bash -c "echo 'informix ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers"

  # Run the Informix install script. During the installation you will be asked for an install dir. You might want to use /opt/IBM/informix1210UC6DE
  sudo ./ids_install -DINSTALL_DIR=/opt/IBM/informix1210UC6DE -DLICENSE_ACCEPTED=TRUE -i silent
  cd ~
  rm -rf /tmp/ifxinstall

  sudo ln -s /opt/IBM/informix1210UC6DE /opt/IBM/informix
  sudo mkdir /opt/IBM/ifxdata
  sudo chown informix:informix /opt/IBM/ifxdata
  sudo chmod 770 /opt/IBM/ifxdata

  sudo apt-get install libaio1
  
  # Setup Informix variables
  export INFORMIXDIR=/opt/IBM/informix
  export PATH=$PATH:$INFORMIXDIR/bin
  export INFORMIXSERVER=ol_informix1210
  export INFORMIXSQLHOSTS=$INFORMIXDIR/etc/sqlhosts
  sudo cp ~/sensor-gateway/inf.env $INFORMIXDIR/etc/inf.env 
  sudo chmod 644 $INFORMIXDIR/etc/inf.env
  sudo chown informix:informix $INFORMIXDIR/etc/inf.env
    # Append the following lines to /home/informix/.bashrc
  sudo bash -c "echo 'export INFORMIXDIR=/opt/IBM/informix' >> /home/informix/.bashrc"
  sudo bash -c "echo 'export PATH=/opt/IBM/informix/bin:$PATH' >> /home/informix/.bashrc"
  sudo bash -c "echo 'export INFORMIXSERVER=ol_informix1210' >> /home/informix/.bashrc"
  sudo bash -c "echo 'export INFORMIXSQLHOSTS=/opt/IBM/informix/etc/sqlhosts' >> /home/informix/.bashrc"

  sudo cp /home/pi/sensor-gateway/sqlhosts $INFORMIXDIR/etc/sqlhosts
  sudo chmod 644 $INFORMIXDIR/etc/sqlhosts
  sudo chown informix:informix $INFORMIXDIR/etc/sqlhosts

  sudo cp /home/pi/sensor-gateway/onconfig $INFORMIXDIR/etc/onconfig 
  sudo chmod 644 $INFORMIXDIR/etc/onconfig
  sudo chown informix:informix $INFORMIXDIR/etc/onconfig

  sudo touch /opt/IBM/ifxdata/rootdbs
  sudo chown informix:informix /opt/IBM/ifxdata/rootdbs
  sudo chmod 660 /opt/IBM/ifxdata/rootdbs
  
    #Start Informix 
  sudo bash -c ". $INFORMIXDIR/etc/inf.env;oninit -iwy"
  #echo "EXECUTE FUNCTION task('modify chunk extendable', '1')" | dbaccess sysadmin -

  #Enable the wire listener for REST calls
  sudo cp /home/pi/sensor-gateway/rest.properties /$INFORMIXDIR/etc/rest.properties
  sudo chown informix:informix /$INFORMIXDIR/etc/rest.properties
  sudo chmod 664 /$INFORMIXDIR/etc/rest.properties

  #Start the wire listener
  sudo bash -c "java -cp $INFORMIXDIR/bin/jsonListener.jar com.ibm.nosql.server.ListenerCLI -config $INFORMIXDIR/etc/rest.properties -logfile $INFORMIXDIR/tmp/restListener.log -start &"

  #fyi, to stop the wire listener
  #java -cp $INFORMIXDIR/bin/jsonListener.jar com.ibm.nosql.server.ListenerCLI -config $INFORMIXDIR/etc/rest.properties -hostname localhost -stop 
fi
