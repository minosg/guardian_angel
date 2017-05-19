HOME="$HOME"
PKG_NAME="zeromq"
SRC_PATH="$HOME/srcs"
DEB_PATH="$SRC_PATH/debs"
TRGT_PATH="$SRC_PATH/$PKG_NAME"

ZMQ_VER="4.1.6"
ZMQ_SRC="https://github.com/zeromq/zeromq4-1/releases/download/v$ZMQ_VER/zeromq-$ZMQ_VER.tar.gz"

PKG_MAINTAINER=minos197@gmail.com
PKG_GROUP=ga
PKG_SOURCE=$ZMQ_SRC
PKG_VERSION=$ZMQ_VER
PKG_DEPENDS=libsodium
PKG_LICENSE=GPLv3
PKG_DESCR="ZeroMQ Library"

#source $HOME/.bash_aliases
set -e
rm -rf ./$PKG_NAME && mkdir $PKG_NAME

cd $PKG_NAME
wget $ZMQ_SRC
tar -zxvf $PKG_NAME-*.tar.gz && pushd $PKG_NAME-*/

# Compile ZeroMQ
./configure
make

## Make a deb for ZeroMQ
echo -e "ldconfig" > postinstall-pak
echo -e "ldconfig" > postremove-pak
echo -e $PKG_DESCR > description-pak
sudo checkinstall --maintainer=$PKG_MAINTAINER  --provides=$PKG_NAME --pkggroup=$PKG_GROUP --pkgsource=$PKG_SOURCE  --pkgversion=$PKG_VERSION --pkglicense=$PKG_LICENSE --requires=$PKG_DEPENDS --nodoc --install=no -y -D make install

DEB_NAME=$(ls $PKG_NAME*.deb)
mv $DEB_NAME $DEB_PATH/$DEB_NAME
cd $DEB_PATH
dpkg-name $DEB_NAME -o
echo "$DEB_PATH/$(ls $PKG_NAME*.deb) created succesfully."

