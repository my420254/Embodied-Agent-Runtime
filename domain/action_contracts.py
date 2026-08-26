from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrimitiveActionContract:
    name: str
    target_keys: tuple[str, ...] = ()


TARGET_LOCATION = "target_location"
TARGET_ITEM = "target_item"
TARGET_CONTAINER = "target_container"
TARGET_DEVICE = "target_device"
TARGET_OBJECT = "target_object"
TARGET_BED = "target_bed"
TARGET_SEAT = "target_seat"
DESTINATION = "destination"
SURFACE = "surface"
WATER_SOURCE = "water_source"
HEATING_DEVICE = "heating_device"


PRIMITIVE_ACTIONS = {
    "NavigateTo": PrimitiveActionContract("NavigateTo", (TARGET_LOCATION,)),
    "Pickup": PrimitiveActionContract("Pickup", (TARGET_ITEM,)),
    "Put": PrimitiveActionContract("Put", (TARGET_ITEM, DESTINATION)),
    "Slice": PrimitiveActionContract("Slice", (TARGET_ITEM, SURFACE)),
    "Heat": PrimitiveActionContract("Heat", (TARGET_ITEM, HEATING_DEVICE)),
    "Clean": PrimitiveActionContract("Clean", (TARGET_ITEM, WATER_SOURCE)),
    "Open": PrimitiveActionContract("Open", (TARGET_CONTAINER,)),
    "Close": PrimitiveActionContract("Close", (TARGET_CONTAINER,)),
    "ToggleOn": PrimitiveActionContract("ToggleOn", (TARGET_DEVICE,)),
    "ToggleOff": PrimitiveActionContract("ToggleOff", (TARGET_DEVICE,)),
    "Read": PrimitiveActionContract("Read", (TARGET_ITEM,)),
    "Observe": PrimitiveActionContract("Observe", (TARGET_OBJECT,)),
    "Type": PrimitiveActionContract("Type", (TARGET_DEVICE,)),
    "Touch": PrimitiveActionContract("Touch", (TARGET_OBJECT,)),
    "Drink": PrimitiveActionContract("Drink", (TARGET_ITEM,)),
    "Sit": PrimitiveActionContract("Sit", (TARGET_SEAT,)),
    "Sleep": PrimitiveActionContract("Sleep", (TARGET_BED,)),
}


HIGH_RISK_BOUND_KEYS = {
    "Slice": (TARGET_ITEM, SURFACE),
    "Heat": (TARGET_ITEM, HEATING_DEVICE),
    "ToggleOn": (TARGET_DEVICE,),
    "Clean": (TARGET_ITEM, WATER_SOURCE),
}


OPENABLE_CONTAINER_TYPES = frozenset(
    {
        "openable_container",
        "heating_device",
        "kettle",
        "washing_machine",
    }
)


NON_PICKUP_CLEAN_TARGET_TYPES = frozenset(
    {
        "surface",
        "countertop",
        "fixture",
        "water_source",
        "openable_container",
        "heating_device",
        "kettle",
        "washing_machine",
    }
)


OPEN_STATE_ALIASES = ("isOpen", "open", "opened")
CLOSED_STATE_ALIASES = ("isClosed", "closed")
TOGGLE_ON_STATE_ALIASES = ("isToggled", "toggled", "isOn", "on", "powered", "poweredOn")
TOGGLE_OFF_STATE_ALIASES = ("isOff", "off")
AVAILABLE_STATE_ALIASES = ("available", "isAvailable", "usable", "isUsable")
UNAVAILABLE_STATE_ALIASES = ("unavailable", "isUnavailable")
