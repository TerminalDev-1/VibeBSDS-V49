# TerminalDev V49 Server

A personal Brawl Stars V49.194 server workspace maintained by
[@TerminalDev-1](https://github.com/TerminalDev-1).

The current server supports the Project BSDS V49 client and has been tested on
an Android device through the home/lobby login flow. It listens on TCP port
`9339` by default.

## Start the server

Requirements:

- Python 3
- A V49.194-compatible client configured to connect to the server computer's
  LAN address on port `9339`

Run:

```powershell
python Core.py
```

The server binds to `0.0.0.0:9339`. If another device is connecting over your
network, allow TCP port `9339` through the host firewall.

## Project status

This is a development and learning project. It is not intended for production
hosting, monetisation, interaction with official services, or use with an
official account.

Client APKs, signing keys, generated builds, logs, and local databases are not
stored in this repository.

## Credits

This repository is derived from
[Zhany4ka/BSDS-V49](https://github.com/Zhany4ka/BSDS-V49), itself based on the
original BSDS work by [CrazorTheCat](https://github.com/CrazorTheCat).

Additional upstream credits:

- [kagenay](https://github.com/kagenay) — Android client tooling
- [HaccerCat](https://github.com/HaccerCat) — crypto/client assistance
- [VitalikObject/OldBrawl](https://github.com/VitalikObject/OldBrawl) — crypto implementation

## Licence

Licensed under the [Apache License 2.0](LICENSE). Upstream attribution and
licence notices are retained.
