# vpnmd

A POSIX compliant daemon for [vpnm](https://github.com/anatolio-deb/vpnm) designed to run as root and perform network-related system calls.

**Note**: vpnmd relies on a [sockets-framework](https://github.com/anatolio-deb/sockets-framework) — «*a simple framework for easy building customized IPC servers*».

# Tests

As vpnmd requires root privileges, it's more reasonable to test it inside a Docker container. That includes building the `Dockerfile` provided in the root of repository:

```
docker build -t vpnmd:testing .
```

And running the testing image with a root privileges:

```
docker run --privileged vpnmd:testing
```

# Build

Using [pyinstaller](https://www.pyinstaller.org/):

```
pyinstaller -F -n vpnmd --hidden-import=libxtwrapper appd.py
```

# Known issues

There's `ioctl(TUNSETIFF) device or resource busy` error while trying to call `ip tuntap del dev tunX mode tun` command inside a testing image, so this test case is skipped, as it passes while being tested on the host.