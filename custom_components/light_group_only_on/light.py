"""Platform to enable modification of light properties without turning on lights that are off, extending core light group."""

from __future__ import annotations

import logging
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

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
    SERVICE_TURN_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DOMAIN = "light_group_only_on"
CONF_STAY_OFF = "stay_off"
CONF_PREVENT_OFF = "prevent_off"

# Validation of the user's configuration
PLATFORM_SCHEMA = LIGHT_GROUP_PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_STAY_OFF, default=False): cv.boolean,
    vol.Optional(CONF_PREVENT_OFF, default=False): cv.boolean
})

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
                config.get(CONF_STAY_OFF),
                config.get(CONF_PREVENT_OFF),
            )
        ]
    )


class LightGroupOnlyOn(LightGroup):
    """Representation of a light group that forwards turn_on (that change state) commands only to on lights."""

    def __init__(self, unique_id, name, entity_ids, mode: bool | None, stay_off: bool = False, prevent_off: bool = False):
        super().__init__(unique_id, name, entity_ids, mode)
        self._stay_off = stay_off
        self._prevent_off = prevent_off

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
        else:
            if self._stay_off:
                _LOGGER.debug("Staying off")
                return

        _LOGGER.debug("Forwarded turn_on command: %s", data)

        await self.hass.services.async_call(
            light.DOMAIN,
            SERVICE_TURN_ON,
            data,
            blocking=True,
            context=self._context,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Forward the turn_off command to all lights in the light group."""

        if self._prevent_off:
            _LOGGER.debug("Preventing off")
            return

        # Set default data
        data = {
            key: value for key, value in kwargs.items() if key in FORWARDED_ATTRIBUTES
        }
        data[ATTR_ENTITY_ID] = self._entity_ids

        _LOGGER.debug("Forwarded turn_off command: %s", data)

        await self.hass.services.async_call(
            light.DOMAIN,
            SERVICE_TURN_OFF,
            data,
            blocking=True,
            context=self._context,
        )
