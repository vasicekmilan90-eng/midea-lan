"""Midea local C3 device."""

import json
import logging
from enum import StrEnum
from typing import Any, ClassVar, Unpack

from midealocal.const import DeviceType
from midealocal.device import MideaDevice, MideaDeviceInitKwargs

from .message import (
    C3DeviceMode,
    C3SilentLevel,
    C3UnitRunMode,
    MessageC3Response,
    MessageQuery,
    MessageQueryBasic,
    MessageQueryDisinfect,
    MessageQueryECO,
    MessageQuerySilence,
    MessageQueryUnitPara,
    MessageSet,
    MessageSetDisinfect,
    MessageSetECO,
    MessageSetSilent,
)

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    """Midea C3 device attributes."""

    zone1_power = "zone1_power"
    zone2_power = "zone2_power"
    dhw_power = "dhw_power"
    zone1_curve = "zone1_curve"
    zone2_curve = "zone2_curve"
    disinfect = "disinfect"
    fast_dhw = "fast_dhw"
    zone_temp_type = "zone_temp_type"
    zone1_room_temp_mode = "zone1_room_temp_mode"
    zone2_room_temp_mode = "zone2_room_temp_mode"
    zone1_water_temp_mode = "zone1_water_temp_mode"
    zone2_water_temp_mode = "zone2_water_temp_mode"
    mode = "mode"
    mode_auto = "mode_auto"
    zone_target_temp = "zone_target_temp"
    dhw_target_temp = "dhw_target_temp"
    room_target_temp = "room_target_temp"
    zone_heating_temp_max = "zone_heating_temp_max"
    zone_heating_temp_min = "zone_heating_temp_min"
    zone_cooling_temp_max = "zone_cooling_temp_max"
    zone_cooling_temp_min = "zone_cooling_temp_min"
    tank_actual_temperature = "tank_actual_temperature"
    room_temp_max = "room_temp_max"
    room_temp_min = "room_temp_min"
    dhw_temp_max = "dhw_temp_max"
    dhw_temp_min = "dhw_temp_min"
    target_temperature = "target_temperature"
    temperature_max = "temperature_max"
    temperature_min = "temperature_min"
    status_heating = "status_heating"
    status_dhw = "status_dhw"
    status_tbh = "status_tbh"
    status_ibh = "status_ibh"
    total_energy_consumption = "total_energy_consumption"
    total_produced_energy = "total_produced_energy"
    outdoor_temperature = "outdoor_temperature"
    temp_tw_in = "temp_tw_in"
    temp_tw_out = "temp_tw_out"
    instant_power0 = "instant_power0"
    silent_mode = "silent_mode"
    silent_level = "silent_level"
    eco_mode = "eco_mode"
    tbh = "tbh"
    error_code = "error_code"
    # --- Extended attributes exposing data already parsed by C3 message bodies ---
    error_code_description = "error_code_description"
    # Notify1 bit flags (device capability / runtime flags)
    heat = "heat"
    cool = "cool"
    dhw = "dhw"
    double_zone = "double_zone"
    room_thermal_support = "room_thermal_support"
    room_thermal_state = "room_thermal_state"
    time_set = "time_set"
    holiday_on = "holiday_on"
    remote_onoff = "remote_onoff"
    tbh_control = "tbh_control"
    sys_energy_ana_en = "sys_energy_ana_en"
    hmi_energy_ana_set_en = "hmi_energy_ana_set_en"
    # Energy / heat pump status
    status_cool = "status_cool"
    # ECO body
    eco_function_state = "eco_function_state"
    eco_timer_state = "eco_timer_state"
    # Disinfect body
    disinfect_run = "disinfect_run"
    # UnitPara body (unit runtime telemetry)
    comp_run_freq = "comp_run_freq"
    fan_speed = "fan_speed"
    unit_mode_run = "unit_mode_run"
    temp_t1 = "temp_t1"
    temp_t2 = "temp_t2"
    temp_t2b = "temp_t2b"
    temp_t3 = "temp_t3"
    temp_t4 = "temp_t4"
    temp_t5 = "temp_t5"
    temp_ta = "temp_ta"
    temp_tp = "temp_tp"
    temp_th = "temp_th"
    temp_tf = "temp_tf"
    temp_tw2 = "temp_tw2"
    temp_tb_t1 = "temp_tb_t1"
    temp_tb_t2 = "temp_tb_t2"
    temp_tsolar = "temp_tsolar"
    pressure_high = "pressure_high"
    pressure_low = "pressure_low"
    water_flow = "water_flow"
    water_pressure = "water_pressure"
    exv_opening = "exv_opening"
    odu_voltage = "odu_voltage"
    dc_current = "dc_current"
    room_rel_hum = "room_rel_hum"
    # Energy totals from UnitPara body
    total_electricity0 = "total_electricity0"
    total_thermal0 = "total_thermal0"
    heat_elec_total_consum0 = "heat_elec_total_consum0"
    heat_elec_total_capacity0 = "heat_elec_total_capacity0"
    instant_renew_power0 = "instant_renew_power0"
    total_renew_power0 = "total_renew_power0"
    # WiFi module identifier (parsed from tail of energy frame)
    wifi_module_serial = "wifi_module_serial"
    # --- Additional low-level diagnostic attributes exposed 1:1 from parser ---
    current_unit_capacity = "current_unit_capacity"
    hydbox_subtype = "hydbox_subtype"
    hydrobox_capacity = "hydrobox_capacity"
    machine_type = "machine_type"
    odu_model = "odu_model"
    odu_plan_vol_lmt = "odu_plan_vol_lmt"
    odu_target_fre = "odu_target_fre"
    fg_capacity_need = "fg_capacity_need"
    fg_usb_info_connect = "fg_usb_info_connect"
    temp_t4a_ver = "temp_t4a_ver"
    t5s = "t5s"
    tas = "tas"
    idu_t1s1 = "idu_t1s1"
    idu_t1s2 = "idu_t1s2"
    zone1_temp_set = "zone1_temp_set"
    zone2_temp_set = "zone2_temp_set"
    zone_terminal_type = "zone_terminal_type"
    pwm_pump_out = "pwm_pump_out"
    sphera_ahs_voltage = "sphera_ahs_voltage"
    disinfect_set_weekday = "disinfect_set_weekday"
    disinfect_start_hour = "disinfect_start_hour"
    disinfect_start_minutes = "disinfect_start_minutes"


class MideaC3Device(MideaDevice):
    """Midea C3 device."""

    _silent_modes: ClassVar[list[str]] = [
        C3SilentLevel.OFF.name.lower(),
        C3SilentLevel.SILENT.name.lower(),
        C3SilentLevel.SUPER_SILENT.name.lower(),
    ]

    def __init__(
        self,
        *,
        customize: str,
        **kwargs: Unpack[MideaDeviceInitKwargs],
    ) -> None:
        """Initialize Midea C3 device."""
        super().__init__(
            device_type=DeviceType.C3,
            **kwargs,
            attributes={
                DeviceAttributes.zone1_power: False,
                DeviceAttributes.zone2_power: False,
                DeviceAttributes.dhw_power: False,
                DeviceAttributes.zone1_curve: False,
                DeviceAttributes.zone2_curve: False,
                DeviceAttributes.disinfect: False,
                DeviceAttributes.fast_dhw: False,
                DeviceAttributes.zone_temp_type: [False, False],
                DeviceAttributes.zone1_room_temp_mode: False,
                DeviceAttributes.zone2_room_temp_mode: False,
                DeviceAttributes.zone1_water_temp_mode: False,
                DeviceAttributes.zone2_water_temp_mode: False,
                DeviceAttributes.silent_mode: False,
                DeviceAttributes.silent_level: C3SilentLevel.OFF.name.lower(),
                DeviceAttributes.eco_mode: False,
                DeviceAttributes.tbh: False,
                DeviceAttributes.mode: 1,
                DeviceAttributes.mode_auto: 1,
                DeviceAttributes.zone_target_temp: [25.0, 25.0],
                DeviceAttributes.dhw_target_temp: 25.0,
                DeviceAttributes.room_target_temp: 30.0,
                DeviceAttributes.zone_heating_temp_max: [55.0, 55.0],
                DeviceAttributes.zone_heating_temp_min: [25.0, 25.0],
                DeviceAttributes.zone_cooling_temp_max: [25.0, 25.0],
                DeviceAttributes.zone_cooling_temp_min: [5.0, 5.0],
                DeviceAttributes.room_temp_max: 60.0,
                DeviceAttributes.room_temp_min: 34.0,
                DeviceAttributes.dhw_temp_max: 60.0,
                DeviceAttributes.dhw_temp_min: 20.0,
                DeviceAttributes.tank_actual_temperature: None,
                DeviceAttributes.target_temperature: [25.0, 25.0],
                DeviceAttributes.temperature_max: [0.0, 0.0],
                DeviceAttributes.temperature_min: [0.0, 0.0],
                DeviceAttributes.total_energy_consumption: None,
                DeviceAttributes.status_heating: None,
                DeviceAttributes.status_dhw: None,
                DeviceAttributes.status_tbh: None,
                DeviceAttributes.status_ibh: None,
                DeviceAttributes.total_produced_energy: None,
                DeviceAttributes.outdoor_temperature: None,
                DeviceAttributes.temp_tw_in: None,
                DeviceAttributes.temp_tw_out: None,
                DeviceAttributes.instant_power0: None,
                DeviceAttributes.error_code: 0,
                DeviceAttributes.error_code_description: "No error",
                DeviceAttributes.heat: False,
                DeviceAttributes.cool: False,
                DeviceAttributes.dhw: False,
                DeviceAttributes.double_zone: False,
                DeviceAttributes.room_thermal_support: False,
                DeviceAttributes.room_thermal_state: False,
                DeviceAttributes.time_set: False,
                DeviceAttributes.holiday_on: False,
                DeviceAttributes.remote_onoff: False,
                DeviceAttributes.tbh_control: False,
                DeviceAttributes.sys_energy_ana_en: False,
                DeviceAttributes.hmi_energy_ana_set_en: False,
                DeviceAttributes.status_cool: None,
                DeviceAttributes.eco_function_state: False,
                DeviceAttributes.eco_timer_state: False,
                DeviceAttributes.disinfect_run: False,
                DeviceAttributes.comp_run_freq: None,
                DeviceAttributes.fan_speed: None,
                DeviceAttributes.unit_mode_run: C3UnitRunMode.OFF.name.lower(),
                DeviceAttributes.temp_t1: None,
                DeviceAttributes.temp_t2: None,
                DeviceAttributes.temp_t2b: None,
                DeviceAttributes.temp_t3: None,
                DeviceAttributes.temp_t4: None,
                DeviceAttributes.temp_t5: None,
                DeviceAttributes.temp_ta: None,
                DeviceAttributes.temp_tp: None,
                DeviceAttributes.temp_th: None,
                DeviceAttributes.temp_tf: None,
                DeviceAttributes.temp_tw2: None,
                DeviceAttributes.temp_tb_t1: None,
                DeviceAttributes.temp_tb_t2: None,
                DeviceAttributes.temp_tsolar: None,
                DeviceAttributes.pressure_high: None,
                DeviceAttributes.pressure_low: None,
                DeviceAttributes.water_flow: None,
                DeviceAttributes.water_pressure: None,
                DeviceAttributes.exv_opening: None,
                DeviceAttributes.odu_voltage: None,
                DeviceAttributes.dc_current: None,
                DeviceAttributes.room_rel_hum: None,
                DeviceAttributes.total_electricity0: None,
                DeviceAttributes.total_thermal0: None,
                DeviceAttributes.heat_elec_total_consum0: None,
                DeviceAttributes.heat_elec_total_capacity0: None,
                DeviceAttributes.instant_renew_power0: None,
                DeviceAttributes.total_renew_power0: None,
                DeviceAttributes.wifi_module_serial: None,
                DeviceAttributes.current_unit_capacity: None,
                DeviceAttributes.hydbox_subtype: None,
                DeviceAttributes.hydrobox_capacity: None,
                DeviceAttributes.machine_type: None,
                DeviceAttributes.odu_model: None,
                DeviceAttributes.odu_plan_vol_lmt: None,
                DeviceAttributes.odu_target_fre: None,
                DeviceAttributes.fg_capacity_need: None,
                DeviceAttributes.fg_usb_info_connect: None,
                DeviceAttributes.temp_t4a_ver: None,
                DeviceAttributes.temp_tf: None,
                DeviceAttributes.t5s: None,
                DeviceAttributes.tas: None,
                DeviceAttributes.idu_t1s1: None,
                DeviceAttributes.idu_t1s2: None,
                DeviceAttributes.zone1_temp_set: None,
                DeviceAttributes.zone2_temp_set: None,
                DeviceAttributes.zone_terminal_type: None,
                DeviceAttributes.pwm_pump_out: None,
                DeviceAttributes.sphera_ahs_voltage: None,
                DeviceAttributes.disinfect_set_weekday: None,
                DeviceAttributes.disinfect_start_hour: None,
                DeviceAttributes.disinfect_start_minutes: None,
            },
        )
        self._default_temperature_step: float = 0.5
        self._temperature_step: float = 0.5
        self.set_customize(customize)

    @property
    def temperature_step(self) -> float | None:
        """Midea C3 device temperature step."""
        return self._temperature_step

    @property
    def silent_modes(self) -> list[str]:
        """Midea C3 device silent modes."""
        return MideaC3Device._silent_modes

    def build_query(self) -> list[MessageQuery]:
        """Midea C3 device build query."""
        return [
            MessageQueryBasic(self._message_protocol_version),
            MessageQueryDisinfect(self._message_protocol_version),
            MessageQuerySilence(self._message_protocol_version),
            MessageQueryECO(self._message_protocol_version),
            MessageQueryUnitPara(self._message_protocol_version),
        ]

    def process_message(self, msg: bytes) -> dict[str, Any]:
        """Midea C3 device process message."""
        message = MessageC3Response(msg)
        _LOGGER.debug("[%s] Received: %s", self.device_id, message)
        new_status = self.update_attributes_from_message(message)
        if "zone_temp_type" in new_status:
            for zone in [0, 1]:
                if self._attributes[DeviceAttributes.zone_temp_type][
                    zone
                ]:  # Water temp mode
                    self._attributes[DeviceAttributes.target_temperature][zone] = (
                        self._attributes[DeviceAttributes.zone_target_temp][zone]
                    )
                    if (
                        self._attributes[DeviceAttributes.mode_auto]
                        == C3DeviceMode.COOL
                    ):  # cooling mode
                        self._attributes[DeviceAttributes.temperature_max][zone] = (
                            self._attributes[DeviceAttributes.zone_cooling_temp_max][
                                zone
                            ]
                        )
                        self._attributes[DeviceAttributes.temperature_min][zone] = (
                            self._attributes[DeviceAttributes.zone_cooling_temp_min][
                                zone
                            ]
                        )
                    elif (
                        self._attributes[DeviceAttributes.mode] == C3DeviceMode.HEAT
                    ):  # heating mode
                        self._attributes[DeviceAttributes.temperature_max][zone] = (
                            self._attributes[DeviceAttributes.zone_heating_temp_max][
                                zone
                            ]
                        )
                        self._attributes[DeviceAttributes.temperature_min][zone] = (
                            self._attributes[DeviceAttributes.zone_heating_temp_min][
                                zone
                            ]
                        )
                else:  # Room temp mode
                    self._attributes[DeviceAttributes.target_temperature][zone] = (
                        self._attributes[DeviceAttributes.room_target_temp]
                    )
                    self._attributes[DeviceAttributes.temperature_max][zone] = (
                        self._attributes[DeviceAttributes.room_temp_max]
                    )
                    self._attributes[DeviceAttributes.temperature_min][zone] = (
                        self._attributes[DeviceAttributes.room_temp_min]
                    )
            if self._attributes[DeviceAttributes.zone1_power]:
                if self._attributes[DeviceAttributes.zone_temp_type][zone]:
                    self._attributes[DeviceAttributes.zone1_water_temp_mode] = True
                    self._attributes[DeviceAttributes.zone1_room_temp_mode] = False
                else:
                    self._attributes[DeviceAttributes.zone1_water_temp_mode] = False
                    self._attributes[DeviceAttributes.zone1_room_temp_mode] = True
            else:
                self._attributes[DeviceAttributes.zone1_water_temp_mode] = False
                self._attributes[DeviceAttributes.zone1_room_temp_mode] = False
            if self._attributes[DeviceAttributes.zone2_power]:
                if self._attributes[DeviceAttributes.zone_temp_type][zone]:
                    self._attributes[DeviceAttributes.zone2_water_temp_mode] = True
                    self._attributes[DeviceAttributes.zone2_room_temp_mode] = False
                else:
                    self._attributes[DeviceAttributes.zone2_water_temp_mode] = False
                    self._attributes[DeviceAttributes.zone2_room_temp_mode] = True
            else:
                self._attributes[DeviceAttributes.zone2_water_temp_mode] = False
                self._attributes[DeviceAttributes.zone2_room_temp_mode] = False
            new_status[DeviceAttributes.zone1_water_temp_mode.value] = self._attributes[
                DeviceAttributes.zone1_water_temp_mode
            ]
            new_status[DeviceAttributes.zone2_water_temp_mode.value] = self._attributes[
                DeviceAttributes.zone2_water_temp_mode
            ]
            new_status[DeviceAttributes.zone1_room_temp_mode.value] = self._attributes[
                DeviceAttributes.zone1_room_temp_mode
            ]
            new_status[DeviceAttributes.zone2_room_temp_mode.value] = self._attributes[
                DeviceAttributes.zone2_room_temp_mode
            ]

        return new_status

    def make_message_set(self) -> MessageSet:
        """Midea C3 device make message set."""
        message = MessageSet(self._message_protocol_version)
        message.zone1_power = self._attributes[DeviceAttributes.zone1_power]
        message.zone2_power = self._attributes[DeviceAttributes.zone2_power]
        message.dhw_power = self._attributes[DeviceAttributes.dhw_power]
        message.mode = self._attributes[DeviceAttributes.mode]
        message.zone_target_temp = self._attributes[DeviceAttributes.zone_target_temp]
        message.dhw_target_temp = self._attributes[DeviceAttributes.dhw_target_temp]
        message.room_target_temp = self._attributes[DeviceAttributes.room_target_temp]
        message.zone1_curve = self._attributes[DeviceAttributes.zone1_curve]
        message.zone2_curve = self._attributes[DeviceAttributes.zone2_curve]
        message.tbh = self._attributes[DeviceAttributes.tbh]
        message.fast_dhw = self._attributes[DeviceAttributes.fast_dhw]
        return message

    def set_attribute(self, attr: str, value: bool | float | str) -> None:
        """Midea C3 device set attribute."""
        message: (
            MessageSet | MessageSetECO | MessageSetSilent | MessageSetDisinfect | None
        ) = None
        if attr in [
            DeviceAttributes.zone1_power,
            DeviceAttributes.zone2_power,
            DeviceAttributes.dhw_power,
            DeviceAttributes.zone1_curve,
            DeviceAttributes.zone2_curve,
            DeviceAttributes.tbh,
            DeviceAttributes.fast_dhw,
            DeviceAttributes.dhw_target_temp,
        ]:
            message = self.make_message_set()
            setattr(message, str(attr), value)
        elif attr == DeviceAttributes.eco_mode:
            message = MessageSetECO(self._message_protocol_version)
            setattr(message, str(attr), value)
        elif attr == DeviceAttributes.disinfect:
            message = MessageSetDisinfect(self._message_protocol_version)
            setattr(message, str(attr), value)
        elif attr in [
            DeviceAttributes.silent_mode.value,
            DeviceAttributes.silent_level.value,
        ]:
            message = MessageSetSilent(self._message_protocol_version)
            if attr == DeviceAttributes.silent_mode.value and isinstance(value, bool):
                message.silent_mode = bool(value)
                message.silent_level = (
                    C3SilentLevel.SILENT
                    if value
                    and self._attributes[DeviceAttributes.silent_level]
                    == C3SilentLevel.OFF.name.lower()
                    else C3SilentLevel[
                        self._attributes[DeviceAttributes.silent_level].upper()
                    ]
                )
            elif attr == DeviceAttributes.silent_level.value and isinstance(value, str):
                normalized_value = value.upper()
                message.silent_level = C3SilentLevel[normalized_value]
                message.silent_mode = normalized_value != C3SilentLevel.OFF.name
        if message is not None:
            self.build_send(message)

    def set_mode(self, zone: int, mode: int) -> None:
        """Midea C3 device set mode."""
        message = self.make_message_set()
        if zone == 0:
            message.zone1_power = True
        else:
            message.zone2_power = True
        message.mode = mode
        self.build_send(message)

    def set_target_temperature(
        self,
        target_temperature: float,
        mode: int | None,
        zone: int | None = None,
    ) -> None:
        """Midea C3 device set target temperature."""
        if zone is None:
            raise ValueError("[C3] Parameter `zone` must be set")

        message = self.make_message_set()
        if self._attributes[DeviceAttributes.zone_temp_type][zone]:
            message.zone_target_temp[zone] = target_temperature
        else:
            message.room_target_temp = target_temperature
        if mode is not None:
            if zone == 0:
                message.zone1_power = True
            else:
                message.zone2_power = True
            message.mode = mode
        self.build_send(message)

    def set_customize(self, customize: str) -> None:
        """Midea C3 device set customize."""
        self._temperature_step = self._default_temperature_step
        if customize and len(customize) > 0:
            try:
                params = json.loads(customize)
                if params and "temperature_step" in params:
                    temp_step = params.get("temperature_step")
                    if isinstance(temp_step, float | int):
                        self._temperature_step = float(temp_step)
                    else:
                        _LOGGER.error(
                            "[%s] Invalid type for temperature_step: %s",
                            self.device_id,
                            temp_step,
                        )
            except json.JSONDecodeError:
                _LOGGER.exception(
                    "[%s] JSON decode error in set_customize",
                    self.device_id,
                )
            self.update_all({"temperature_step": self._temperature_step})


class MideaAppliance(MideaC3Device):
    """Midea C3 appliance."""
