## Using Grid'5000 for continuous integration

This script will handle the deployment of ubuntu on either paravance, grisou, graphene or griffon clusters on Grid'5000.

This is a ubuntu tweaked from kaenv3's ubuntu-x64-1404, with the necessary package to deploy a virtual machine via Vagrant and VirtualBox, and execute Rally scripts.

Once ubuntu is ready, the script downloads the slave agent for CI's Jenkins and relays the ssh connection to the deployed node.