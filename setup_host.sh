#!/bin/bash
set -x
script_dir=$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)

# This script sets up a Ubuntu host to be able to create the image by
# installing all of the necessary files. It assumes a host with
# passwordless sudo

# Install a bunch of packages we need

if [ $(lsb_release -rs) == "18.04" ]; then
    rel_deps="libncurses5-dev lib32ncurses5"
elif [ $(lsb_release -rs) == "20.04" ]; then
    rel_deps="libncurses6 lib32ncurses6"
else
    echo "Error: Please use Ubuntu 20.04 or Ubuntu 18.04."
    exit 1
fi

read -d '' PACKAGES <<EOT
bc
libtool-bin
gperf
bison
flex
texi2html
texinfo
help2man
gawk
libtool
build-essential
automake
libncurses5-dev
libglib2.0-dev
libfdt-dev
device-tree-compiler
qemu-user-static
binfmt-support
multistrap
git
lib32z1
lib32stdc++6
libssl-dev
kpartx
dosfstools
nfs-common
zerofree
u-boot-tools
rpm2cpio
curl
docker-ce
docker-ce-cli
containerd.io
libsdl1.2-dev
libpixman-1-dev
libc6-dev
chrpath
socat
zlib1g-dev
zlib1g:i386
unzip
rsync
python3-pip
gcc-multilib
xterm
net-tools
libidn11
EOT
set -e

sudo apt-get update

# Setup docker and containerd using repository before installing them
sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu xenial stable"
sudo apt-get update

sudo dpkg --add-architecture i386
sudo apt-get update
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/ppa
sudo apt-get update
sudo apt-get install -y $PACKAGES

# Double-check docker can run with or without sudo
sudo service docker start
sudo chmod 777 /var/run/docker.sock
docker run hello-world
sudo docker run hello-world

# Install up-to-date versions of crosstool and qemu
if [ -e tools ]; then
  rm -rf tools
fi

mkdir tools
cd tools/

ctver="1.24.0"
wget http://crosstool-ng.org/download/crosstool-ng/crosstool-ng-$ctver.tar.bz2
tar -xf crosstool-ng-$ctver.tar.bz2
cd crosstool-ng-$ctver
./configure --prefix=/usr/bin/crosstool-ng
make
sudo make install
cd ..

qemuver="6.2.0"
wget http://wiki.qemu-project.org/download/qemu-$qemuver.tar.bz2 --no-check-certificate
tar -xf qemu-$qemuver.tar.bz2
cd qemu-$qemuver
./configure --target-list=arm-linux-user,aarch64-linux-user \
	--prefix=/usr/bin/qemu --static
make && sudo make install
# Create the symlink that ubuntu expects
cd /usr/bin/qemu/bin
sudo rm -rf qemu-arm-static qemu-aarch64-static
sudo ln -s qemu-arm qemu-arm-static
sudo ln -s qemu-aarch64 qemu-aarch64-static
cd ~

# Create gmake symlink to keep Vitis happy
cd /usr/bin
if ! which gmake
then
  sudo ln -s make gmake
fi

# make sure resolv.conf is where it's going to be expected in chroot
if [ ! -f /run/systemd/resolve/stub-resolv.conf ]; then
    sudo mkdir -p /run/systemd/resolve
    sudo cp -L /etc/resolv.conf /run/systemd/resolve/stub-resolv.conf
fi

# update setuptools
sudo -H python3 -m pip install --upgrade "setuptools>=24.2.0"
# install dependencies required to build pynq sdist
sudo -H python3 -m pip install numpy cffi

echo 'PATH=/usr/bin/qemu/bin:/usr/bin/crosstool-ng/bin:$PATH' >> ~/.profile

echo "Now install Vitis and Petalinux."
echo "Re-login to  ensure the environment is properly set up."
