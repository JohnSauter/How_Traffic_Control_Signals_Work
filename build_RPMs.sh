#!/bin/bash
# File: build_RPMs.sh, author: John Sauter, date: November 30, 2024.
# Build the RPMs for How_Traffic_signals_work.

# Requires fedora-packager, rpmdevtools, copr-cli.
# Don't forget to tell copr-cli about your copr API token.
# See https://developer.fedoraproject.org/deployment/copr/copr-cli.html.

rm -rf ~/rpmbuild
mkdir -p ~/rpmbuild
mkdir -p ~/rpmbuild/SOURCES
mkdir -p ~/rpmbuild/SRPMS
mkdir -p ~/rpmbuild/RPMS/noarch

pushd ~/rpmbuild
# Set the umask so files created will not have strange permissions.
umask 022
# Clean out any old versions of the application.
rm -f SOURCES/*
rm -f SRPMS/*
rm -f RPMS/noarch/*
# Copy in the new tarball and spec file.
popd
cp -v How_Traffic_Control_Signals_Work-*.tar.gz ~/rpmbuild/SOURCES/
cp -v How_Traffic_Control_Signals_Work.spec ~/rpmbuild/SOURCES/
pushd ~/rpmbuild/SOURCES
# Set the file protections to the proper values.
chmod 0644 How_Traffic_Control_Signals_Work-*.tar.gz
chmod 0644 How_Traffic_Control_Signals_Work.spec
# Build the source RPM.
echo "Building source RPM."
rpmbuild -bs How_Traffic_Control_Signals_Work.spec
# Copy back the source RPM so it can be copied to github.
popd
cp -v ~/rpmbuild/SRPMS/How_Traffic_Control_Signals_Work-*.src.rpm .
# Make sure it is OK.
echo "Validating source RPM."
rpmlint How_Traffic_Control_Signals_Work-*.src.rpm
# Further test the source RPM by building and testing the binary RPMs.
pushd ~/rpmbuild/SOURCES
echo "Building binary RPM."
rpmbuild -bb How_Traffic_Control_Signals_Work.spec
popd
# Perform validity checking on the RPMs.
pushd ~/rpmbuild/SRPMS
echo "Validating source RPM again."
rpmlint How_Traffic_Control_Signals_Work-*.src.rpm
pushd ../RPMS/noarch/
echo "Validating binary RPM."
rpmlint How_Traffic_Control_Signals_Work-*.rpm

# End of file build_RPMs.sh
