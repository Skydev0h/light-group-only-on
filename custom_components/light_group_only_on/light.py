"""Platform to enable modification of light properties without turning on lights that are off, extending core light group."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import light
from homeassistant.components.group.light import (
    CONF_ALL,
    FORWARDED_ATTRIBUTES,
    PLATFORM_SCHEMA as LIGHT_GROUP_PLATFORM_SCHEMA,
    LightGroup,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_ENTITIES,
    CONF_NAME,
    CONF_UNIQUE_ID,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DOMAIN = "light_group_only_on"

# Validation of the user's configuration
PLATFORM_SCHEMA = LIGHT_GROUP_PLATFORM_SCHEMA

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Initialize light_group_only_on platform."""
    async_add_entities(
        [
            LightGroupOnlyOn(
                config.get(CONF_UNIQUE_ID),
                config[CONF_NAME],
                config[CONF_ENTITIES],
                config.get(CONF_ALL),
            )
        ]
    )


class LightGroupOnlyOn(LightGroup):
    """Representation of a light group that forwards turn_on (that change state) commands only to on lights."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Forward the turn_on command to all lights in the light group."""

        # Set default data
        data = {
            key: value for key, value in kwargs.items() if key in FORWARDED_ATTRIBUTES
        }
        data[ATTR_ENTITY_ID] = self._entity_ids

        # Check if any lights are on
        lights_on = [
            state
            for entity_id in self._entity_ids
            if (state := self.hass.states.get(entity_id)) is not None
            and state.state == STATE_ON
        ]

        entity_ids = [state.entity_id for state in lights_on]
        # Check if there are currently lights turned on
        # We need this, otherwise lights could never be turned on
        if entity_ids:
            # Change the target of the command only to the lights that are currently on
            data[ATTR_ENTITY_ID] = entity_ids

        _LOGGER.debug("Forwarded turn_on command: %s", data)

        await self.hass.services.async_call(
            light.DOMAIN,
            SERVICE_TURN_ON,
            data,
            blocking=True,
            context=self._context,
        )
