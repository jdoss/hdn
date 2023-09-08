# HDN

HDN is CLI tool for sending notification messages to [D-Bus](https://www.freedesktop.org/wiki/Software/dbus/) on a Linux desktop. It was originally built so I could use Home Assistant to send alerts to my desktop when certain events in my house change and it was named `hass-dbus-notify`. Since it can be used without Home Assistant it was renamed HDN. As a command line tool you can automate sending messages to D-Bus for almost anything.

Under the hood it uses [Jeepeny](https://jeepney.readthedocs.io/en/latest/index.html) which is a pure Python 3 implementation of the D-Bus protocol. It does all of the heavy lifting for HDN. Since HDN only requires Python 3, you do not need to install any system packages to interface with D-Bus. :tada:

## Install

```bash
pip install hdn
```

## Usage

### Send

The first command of HDN is `send`. It can be used via the CLI to send messages to D-Bus. It also can read environment variables for it's configuration. This is the more fully featured command since it fully uses [Typer's](https://typer.tiangolo.com/) features to ensure the data for each option is correct.

Required options

* --summary            TEXT     Summary of the notification. [env var: HDN_SUMMARY] [required]
* --body               TEXT     Body of the notification. [env var: HDN_BODY] [required]

Optional options

* --urgency            TEXT     Urgency: low, normal, critical [env var: HDN_URGENCY] [default: normal]
* --object-path        TEXT     Object path [env var: HDN_OBJECT_PATH] [default: /org/freedesktop/Notifications]
* --bus-name           TEXT     Bus name [env var: HDN_BUS_NAME] [default: org.freedesktop.Notifications]
* --interface          TEXT     Interface [env var: HDN_INTERFACE] [default: org.freedesktop.Notifications]
* --message-bus        TEXT     Message bus: session, system [env var: HDN_MESSAGE_BUS] [default: session]
* --icon               TEXT     Message icon [env var: HDN_ICON] [default: dialog-warning]
* --expire             INTEGER  Message expiration (seconds) [env var: HDN_EXPIRE] [default: 3]
* --help                        Show the message and exit.

### JSON

The second command of HDN is `json`. It can be used to read a JSON data from a file or stdin. It lightly uses Typer for the command but any options that are fed in via JSON are lightly sanity checked before being processed by HDN and sent to D-Bus. Expect weird things to happen if you send unexpected data in your values. At a minimum the required keys in your JSON need to be:

```json
{
  "summary": "Minimal example summary",
  "body": "Minimal example body"
}
```

Here is a full example of a JSON payload that can be processed by HDN:

```json
{
  "summary": "Full example summary",
  "body": "Full example body",
  "urgency": "critical",
  "object_path": "/org/freedesktop/Notifications",
  "bus_name": "org.freedesktop.Notifications",
  "interface": "org.freedesktop.Notifications",
  "message_bus": "session",
  "icon": "dialog-warning",
  "expire": 20
}
```

See the `examples` directory for more samples of JSON that are used in testing.

## Debugging D-Bus

If you want to see what is going on with your messages you can use `dbus-monitor` to watch the bus in real time.

```bash
dbus-monitor interface=org.freedesktop.Notifications
```

## Reference

* [D-Bus Basic Design](https://specifications.freedesktop.org/notification-spec/latest/ar01s02.html)
* [D-Bus Protocol](https://specifications.freedesktop.org/notification-spec/latest/ar01s09.html)
* [freedesktop.org Icon Names](https://specifications.freedesktop.org/icon-naming-spec/*icon-naming-spec-latest.html)

## License

MIT License

Copyright (c) 2023 Joe Doss

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
