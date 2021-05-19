# vpnmd

A POSIX compliant daemon of an alternative [VPNManager](https://vpn-m.com/) client for Linux CLI.

# Build

Using [pyinstaller](https://www.pyinstaller.org/):

```
pyinstaller -F -n vpnmd --hidden-import=libxtwrapper appd.py
```

## To-do

- Automated testing
- DNS forwarding

# Tests

Tested manually on Ubuntu Linux 18.04 bionic.