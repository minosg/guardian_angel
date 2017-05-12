HOME="/home/pi"
PKG_NAME="libsodium"
SRC_PATH="$HOME/srcs"
DEB_PATH="$SRC_PATH/debs"
TRGT_PATH="$SRC_PATH/$PKG_NAME"
LIBSODIUM_VER="1.0.12"
LIBSODIUM_SRC="https://github.com/jedisct1/libsodium/releases/download/$LIBSODIUM_VER/libsodium-$LIBSODIUM_VER.tar.gz"

PKG_MAINTAINER=minos197@gmail.com
PKG_GROUP=ga
PKG_SOURCE=$LIBSODIUM_SRC
PKG_VERSION=$LIBSODIUM_VER
PKG_LICENSE=ISC
PKG_DESCR="Libsodium Library"

#source $HOME/.bash_aliases
set -e
rm -rf ./$PKG_NAME && mkdir $PKG_NAME

cd $PKG_NAME
wget $LIBSODIUM_SRC
tar -zxvf $PKG_NAME-*.tar.gz && pushd $PKG_NAME-*/

# Compile Libsodium
./configure
make

## Make a deb of libsodium
echo -e "ldconfig" > postinstall-pak
echo -e "ldconfig" > postremove-pak
echo -e $PKG_DESCR > description-pak
sudo checkinstall --maintainer=$PKG_MAINTAINER  --provides=$PKG_NAME --pkggroup=$PKG_GROUP --pkgsource=$PKG_SOURCE  --pkgversion=$PKG_VERSION --pkglicense=$PKG_LICENSE --nodoc --install=no -y -D make install

DEB_NAME=$(ls $PKG_NAME*armhf.deb)
mv $DEB_NAME $DEB_PATH/$DEB_NAME
cd $DEB_PATH
dpkg-name $DEB_NAME -o
echo "$DEB_PATH/$(ls $PKG_NAME*armhf.deb) created succesfully."

