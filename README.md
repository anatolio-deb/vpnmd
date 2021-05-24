# vpnmd

A POSIX compliant daemon for [an alternative VPN Manager Linux CLI client](https://github.com/anatolio-deb/vpnm).

# Build

Using [pyinstaller](https://www.pyinstaller.org/):

```
pyinstaller -F -n vpnmd --hidden-import=libxtwrapper appd.py
```

## To-do

- Automated testing

# Tests

Tested manually on Ubuntu Linux 18.04 bionic.