# vpnmd

A POSIX compliant daemon for [vpnm](https://github.com/anatolio-deb/vpnm) designed to run as root and perform network-related system calls.

**Note**: vpnmd relies on a [sockets-framework](https://github.com/anatolio-deb/sockets-framework) — «*a simple framework for easy building and controlling custom daemons suited with API accessible over IPC*».

# Building and installing from the source

Clone this repository:

```
git clone https://github.com/anatolio-deb/vpnmd
```

Install [poetry](https://python-poetry.org/):

```
pip install poetry
```

Recreate a virtual environment:

```
poetry install
```

Build using [pyinstaller](https://www.pyinstaller.org/):

```
poetry run pyinstaller -F -n vpnmd --clean --hidden-import=libxtwrapper --distpath ~/.var/local/bin --workpath /tmp --specpath /tmp vpnmd/appd.py
```

Symlink the binary:

```
sudo ln -sf ~/.var/local/bin/vpnmd /var/local/bin/vpnmd
```

 Install and run via systemd:

```
sudo cp ./vpnmd.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now vpnmd
```

# Testing

As vpnmd requires root privileges, it's reasonable to test it inside a Docker container. That includes building the `Dockerfile` provided in the root of repository:

```
docker build -t vpnmd:testing .
```

And running the testing image with a root privileges:

```
docker run --privileged vpnmd:testing
```

## Known issues

There's `ioctl(TUNSETIFF) device or resource busy` error while trying to call `ip tuntap del dev tunX mode tun` command inside a testing image, so this test case is skipped, as it passes while being tested on the host.
