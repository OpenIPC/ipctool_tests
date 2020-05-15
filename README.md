# PoC for determine good CI practice for the project

## Installation

Disable host checking:

In your ~/.ssh/config (if this file doesn't exist, just create it):

```
Host *
    StrictHostKeyChecking no
    ConnectTimeout 10
```

## Usage

* To run only test against specific hardware add parameter with site and
  specific id `"ipc_chip_test.py::test_zftlab[HI3518EV200+JXF22]"`
