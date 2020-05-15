# PoC for determine good CI practice for the project

## Installation

Disable host checking:

In your ~/.ssh/config (if this file doesn't exist, just create it):

```
Host *
    StrictHostKeyChecking no
    ConnectTimeout 10
```
