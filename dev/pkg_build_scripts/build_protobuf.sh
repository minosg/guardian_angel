
HOME="$HOME"
PKG_NAME="protobuf"
SRC_PATH="$HOME/srcs"
DEB_PATH="$SRC_PATH/debs"
TRGT_PATH="$SRC_PATH/$PKG_NAME"
VER="3.3.0"
SRC="https://github.com/google/protobuf.git"

PKG_MAINTAINER=minos197@gmail.com
PKG_GROUP=ga
PKG_SOURCE=$SRC
PKG_VERSION=$VER
PKG_LICENSE=BSD
PKG_DESCR="Google's Protocol Buffer"

set -e
source ./build_functions
rm -rf $TRGT_PATH

# Delete old files
rm -rf $SRC_PATH/$PKG_NAME

mkdir -p $SRC_PATH $DEB_PATH


# Download and install dependencies
git clone --recursive -b v$VER $SRC $PKG_NAME
cd $PKG_NAME

./autogen.sh
./configure
make

## Make a deb for Protobuf
echo -e "ldconfig" > postinstall-pak
echo -e "ldconfig" > postremove-pak
echo -e $PKG_DESCR > description-pak
sudo checkinstall --maintainer=$PKG_MAINTAINER  --provides=$PKG_NAME --pkggroup=$PKG_GROUP --pkgsource=$PKG_SOURCE  --pkgversion=$PKG_VERSION --pkglicense=$PKG_LICENSE --requires=$PKG_DEPENDS --nodoc --install=no -y -D make install

sudo chown $(whoami) ./*.deb

rm -rf x1
# Extrac the datafiles
dpkg -x $(ls protobuf*.deb) ./x1

# Extract the controll file
#ar p $(ls protobuf*.deb) | tar -xz -C ./x1/DEBIAN
dpkg-deb -e $(ls protobuf*.deb)
rm DEBIAN/conffiles
mv DEBIAN ./x1/

# Create a temporary directory to pretend it is our local python install
mkdir -p $TRGT_PATH/x1/usr/lib/python2.7/site-packages/
cd python

# Run the python installer
export PYTHONPATH=$TRGT_PATH/x1/usr/lib/python2.7/site-packages/
python setup.py install --cpp_implementation --prefix=$TRGT_PATH/x1/usr/

# Move the folder to a debian based layout
mv $TRGT_PATH/x1/usr/lib/python2.7/site-packages/ $TRGT_PATH/x1/usr/lib/python2.7/dist-packages/
mv $TRGT_PATH/x1/usr/lib/python2.7/dist-packages/proto*/google $TRGT_PATH/x1/usr/lib/python2.7/dist-packages/

# Cleanup easy install related files
rm -f  $TRGT_PATH/x1/usr/lib/python2.7/dist-packages/*.pth
rm -f  $TRGT_PATH/x1/usr/lib/python2.7/dist-packages/*.py*
rm -rf  $TRGT_PATH/x1/usr/bin
rm -rf $TRGT_PATH/x1/usr/lib/python2.7/dist-packages/*.egg

# create final deb
rm -rf $DEB_PATH/$PKG_NAME
cd $DEB_PATH/
#deb-setup $PKG_NAME

mkdir -p $DEB_PATH/$PKG_NAME
mv $TRGT_PATH/x1/* $DEB_PATH/$PKG_NAME

# Edit debian files
#echo -e "ldconfig\n">> $DEB_PATH/$PKG_NAME/DEBIAN/postinst
#echo -e "ldconfig\n" >>$DEB_PATH/$PKG_NAME/DEBIAN/postrm
#sed -i '/Installed-Size*:/d' $DEB_PATH/$PKG_NAME/DEBIAN/control

# fix permissions
chmod 775 $DEB_PATH/$PKG_NAME/DEBIAN/postrm
chmod 775 $DEB_PATH/$PKG_NAME/DEBIAN/postinst

cd $DEB_PATH/
deb-build $PKG_NAME
