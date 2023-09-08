# SPDX-License-Identifier: MIT
#
# Copyright (c) 2023 Joe Doss <joe@solidadmin.com> All Rights Reserved.

import json
import sys
from typing import Optional

import typer
from jeepney import DBusAddress, new_method_call
from jeepney.io.blocking import open_dbus_connection
from typing_extensions import Annotated

__version__ = "0.0.1"

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    epilog="Made in [pale_turquoise1]✶✶✶✶[/pale_turquoise1][red1]Chicago[/red1][pale_turquoise1]✶✶✶✶[/pale_turquoise1]  〜 (c) 2023 Joe Doss",  # noqa: E501
)


@app.callback(invoke_without_command=True)
def main(
    version: Annotated[Optional[bool], typer.Option("--version")] = None,
):
    if version:
        print(f"hdn version: {__version__}")
        raise typer.Exit()


def send_dbus_notification(
    summary: str,
    body: str,
    urgency: int,
    object_path: str,
    bus_name: str,
    interface: str,
    message_bus: str,
    icon: str,
    expire: int,
) -> dict:
    args_map = locals()

    if expire:
        expire_timeout: int = int(expire * 1000)
    else:
        expire_timeout: int = -1

    urgency_map: dict = {"low": 0, "normal": 1, "critical": 2}

    if urgency in urgency_map:
        urgency_int: int = urgency_map[urgency]
    else:
        print(f"Invalid urgency setting: {urgency}")
        raise typer.Exit(code=1)

    if message_bus not in ["session", "system"]:
        print(f"Invalid message bus setting: {message_bus}")
        raise typer.Exit(code=1)

    bus_address = DBusAddress(
        object_path,
        bus_name=bus_name,
        interface=interface,
    )

    connection = open_dbus_connection(bus=message_bus.upper())

    notification = new_method_call(
        bus_address,
        "Notify",
        "susssasa{sv}i",
        (
            "hdn",
            0,  # Replace
            icon,  # Icon
            summary,
            body,
            [],  # Actions
            {"urgency": ("u", urgency_int)},  # Hints
            expire_timeout,  # expire_timeout
        ),
    )

    reply = connection.send_and_get_reply(notification)

    if reply.header.message_type == reply.header.message_type.error:
        json_data: dict = {
            "success": False,
            "message": reply.body[0].replace("\u201c", "").replace("\u201d", ""),
        }
        notification_data = json_data | args_map
    else:
        json_data: dict = {"success": True, "dbus_message_id": reply.body[0]}
        notification_data = json_data | args_map

    connection.close()
    return notification_data


@app.command()
def send(
    summary: Annotated[
        str,
        typer.Option(
            show_default=False,
            help="Summary of the notification.",
            envvar="HDN_SUMMARY",
        ),
    ],
    body: Annotated[
        str,
        typer.Option(show_default=False, help="Body of the notification.", envvar="HDN_BODY"),
    ],
    urgency: Annotated[
        str,
        typer.Option(help="Urgency: low, normal, critical", envvar="HDN_URGENCY"),
    ] = "normal",
    object_path: Annotated[
        str,
        typer.Option(help="Object path", envvar="HDN_OBJECT_PATH"),
    ] = "/org/freedesktop/Notifications",
    bus_name: Annotated[
        str,
        typer.Option(help="Bus name", envvar="HDN_BUS_NAME"),
    ] = "org.freedesktop.Notifications",
    interface: Annotated[
        str,
        typer.Option(help="Interface", envvar="HDN_INTERFACE"),
    ] = "org.freedesktop.Notifications",
    message_bus: Annotated[
        str,
        typer.Option(help="Message bus: session, system ", envvar="HDN_MESSAGE_BUS"),
    ] = "session",
    icon: Annotated[
        str,
        typer.Option(
            help="Message Icon: See https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html for a full list",  # noqa: E501
            envvar="HDN_ICON",
        ),
    ] = "dialog-warning",
    expire: Annotated[
        int,
        typer.Option(help="Message expiration (seconds)", envvar="HDN_EXPIRE"),
    ] = "3",
):
    """
    [green]Send[/green] a notification to D-BUS. :megaphone:
    """

    notification = send_dbus_notification(
        summary,
        body,
        urgency,
        object_path,
        bus_name,
        interface,
        message_bus,
        icon,
        expire,
    )

    print(json.dumps(notification))


def process_json(json_data: str) -> dict:
    """
    Processes JSON data from a file or stdin
    """
    try:
        if sys.stdin.isatty():
            with open(f"{json_data}", "rb") as opened_file:
                json_loaded = json.load(opened_file)
        else:
            json_loaded = json.load(json_data)

        return json_loaded
    except ValueError as err:
        print("The JSON data is invalid: %s" % err)
        raise typer.Exit(1)


@app.command("json")
def input_json(
    data: str = typer.Argument(
        ... if sys.stdin.isatty() else sys.stdin.read().strip(),
        help="Reads a JSON data from a file or stdin and sends a D-BUS notification.",
        show_default=False,
    ),
):
    """
    Process [green]JSON[/green] data from stdin or file and send a notification to D-BUS. :desktop_computer:
    """
    processed_json = process_json(data)

    if not all(keys in processed_json for keys in ("summary", "body")):
        print("The keys: summary and body are required! Check your JSON!")
        raise typer.Exit(1)

    notify_data = {
        "summary": processed_json.get("summary"),
        "body": processed_json.get("body"),
        "urgency": processed_json.get("urgency", "normal"),
        "object_path": processed_json.get("object_path", "/org/freedesktop/Notifications"),
        "bus_name": processed_json.get("bus_name", "org.freedesktop.Notifications"),
        "interface": processed_json.get("interface", "org.freedesktop.Notifications"),
        "message_bus": processed_json.get("message_bus", "session"),
        "icon": processed_json.get("icon", "dialog-warning"),
        "expire": processed_json.get("expire", 3),
    }

    notification = send_dbus_notification(
        notify_data["summary"],
        notify_data["body"],
        notify_data["urgency"],
        notify_data["object_path"],
        notify_data["bus_name"],
        notify_data["interface"],
        notify_data["message_bus"],
        notify_data["icon"],
        notify_data["expire"],
    )

    print(json.dumps(notification))


if __name__ == "__main__":
    app()
