"""Midea local C3 message."""

from enum import IntEnum

from midealocal.const import DeviceType
from midealocal.message import (
    ListTypes,
    MessageBody,
    MessageRequest,
    MessageResponse,
    MessageType,
)

TEMP_NEG_VALUE = 127
ECO_FUNCTION_STATE_MASK = 0x01
ECO_TIMER_STATE_MASK = 0x02


class C3SilentLevel(IntEnum):
    """C3 Silent Level."""

    OFF = 0x0
    SILENT = 0x1
    SUPER_SILENT = 0x3


class C3DeviceMode(IntEnum):
    """C3 Device Mode."""

    COOL = 2
    HEAT = 3


class C3FanSpeed(IntEnum):
    """C3 outdoor unit fan speed levels.

    Values correspond to raw_byte * 10 (parser scales
    ``body[data_offset + 3]`` by 10 to expose these values).
    Exact naming for level 1..4 is not confirmed by any publicly
    available documentation for the Galmet Prima 06 GT model - kept
    generic until an authoritative source is available.
    """

    # OFF added after field verification against wired HMI:
    # compressor idle -> raw byte 0 (which fell back to LEVEL_2).
    OFF = 0
    LEVEL_1 = 10
    LEVEL_2 = 20
    LEVEL_3 = 30
    LEVEL_4 = 40


class C3UnitRunMode(IntEnum):
    """C3 unit actual running mode.

    Reported via Modbus register 101 (V4.7):
    ``0: off, 2: cooling, 3: heating``.
    """

    OFF = 0
    COOL = 2
    HEAT = 3


# Error code lookup (source: official Modbus V4.7 documentation, table 1).
# Format: raw_value -> (display_code, human_description).
# NOTE: 4 codes (Hd, HE, L2, L8) have ambiguous descriptions in the source
# PDF due to two-column layout extraction - kept as "unknown" until an
# authoritative source is available.
C3_ERROR_CODE_TABLE: dict[int, tuple[str, str]] = {
    1: ("E0", "Water flow fault (E8 displayed 3 times)"),
    2: ("E1", "Outlet water temp. sensor for Zone 2 (Tw2) fault"),
    3: ("E2", "Communication fault between controller and hydraulic module"),
    4: ("E3", "Final outlet water temp. sensor (T1) fault"),
    5: ("E4", "Water tank temp. sensor (T5) fault"),
    6: ("E5", "Condenser outlet refrigerant temp. sensor (T3) fault"),
    7: ("E6", "Ambient temp. sensor (T4) fault"),
    8: ("E7", "Buffer tank up temp. sensor (Tbt1) fault"),
    9: ("E8", "Water flow failure"),
    10: ("E9", "Suction temp. sensor (Th) fault"),
    11: ("EA", "Discharge temp. sensor (Tp) fault"),
    12: ("Eb", "Solar temp. sensor (Tsolar) fault"),
    13: ("Ec", "Buffer tank low temp. sensor (Tbt2) fault"),
    14: ("Ed", "Inlet water temp. sensor (Tw_in) malfunction"),
    15: ("EE", "Hydraulic module EEPROM failure"),
    20: ("P0", "Low pressure switch protection"),
    21: ("P1", "High pressure switch protection"),
    23: ("P3", "Compressor overcurrent protection"),
    24: ("P4", "High discharge temperature protection"),
    25: ("P5", "|Tw_out - Tw_in| value too big protection"),
    26: ("P6", "Inverter module protection"),
    31: ("Pb", "Anti-freeze mode"),
    33: ("Pd", "High refrigerant outlet temp. protection of condenser"),
    38: ("PP", "Tw_out - Tw_in unusual protection"),
    39: ("H0", "Communication fault: hydraulic PCB B <-> main control PCB B"),
    40: ("H1", "Communication fault: inverter PCB A <-> main control PCB B"),
    41: ("H2", "Refrigerant liquid temp. sensor (T2) fault"),
    42: ("H3", "Refrigerant gas temp. sensor (T2B) fault"),
    43: ("H4", "Three times P6 (L0/L1) protection"),
    44: ("H5", "Room temp. sensor (Ta) fault"),
    45: ("H6", "DC fan motor fault"),
    46: ("H7", "Voltage protection"),
    47: ("H8", "Pressure sensor fault"),
    48: ("H9", "Speed difference > 15Hz between front and back clock"),
    49: ("HA", "Speed difference > 15Hz between real and setting speed"),
    50: ("Hb", "3 times PP protection and Tw_out < 7C"),
    52: ("Hd", "Unknown / description unclear in source document"),
    53: ("HE", "Unknown / description unclear in source document"),
    54: ("HF", "Inverter module board EEPROM fault"),
    55: ("HH", "H6 displayed 10 times in 2 hours"),
    57: ("HP", "Low pressure protection (Pe<0.6) occurred 3 times in 1 hour"),
    65: ("C7", "Transducer module temperature too high protection"),
    112: ("bH", "PED PCB fault"),
    116: ("F1", "Low DC generatrix voltage protection"),
    134: ("L0", "Module protection"),
    135: ("L1", "DC generatrix low voltage protection"),
    136: ("L2", "Unknown / description unclear in source document"),
    138: ("L4", "MCE fault"),
    139: ("L5", "Zero speed protection"),
    141: ("L7", "Phase sequence fault / phase loss (3-phase only)"),
    142: ("L8", "Unknown / description unclear in source document"),
    143: ("L9", "Unknown / description unclear in source document"),
}


class MessageC3Base(MessageRequest):
    """C3 message base."""

    def __init__(
        self,
        protocol_version: int,
        message_type: MessageType,
        body_type: ListTypes,
    ) -> None:
        """Initialize C3 message base."""
        super().__init__(
            device_type=DeviceType.C3,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type,
        )

    @property
    def _body(self) -> bytearray:
        raise NotImplementedError


class MessageQuery(MessageC3Base):
    """C3 message query."""

    def __init__(self, protocol_version: int, body_type: ListTypes) -> None:
        """Initialize C3 message query."""
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=body_type,
        )

    @property
    def _body(self) -> bytearray:
        return bytearray([])


class MessageQueryBasic(MessageQuery):
    """C3 Message query basic."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message query basic."""
        super().__init__(protocol_version, ListTypes.X01)


class MessageQuerySilence(MessageQuery):
    """C3 Message query silence."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message query silence."""
        super().__init__(protocol_version, ListTypes.X05)


class MessageQueryECO(MessageQuery):
    """C3 Message query ECO."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message query silence."""
        super().__init__(protocol_version, ListTypes.X07)


class MessageQueryInstall(MessageQuery):
    """C3 Message query INSTALL."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message query silence."""
        super().__init__(protocol_version, ListTypes.X08)


class MessageQueryDisinfect(MessageQuery):
    """C3 Message query Disinfect."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message query silence."""
        super().__init__(protocol_version, ListTypes.X09)


class MessageQueryUnitPara(MessageQuery):
    """C3 Message query UNITPARA."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message query silence."""
        super().__init__(protocol_version, ListTypes.X10)


class MessageQueryHMIPara(MessageQuery):
    """C3 Message query HMIPARA."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message query silence."""
        super().__init__(protocol_version, ListTypes.X0A)


class MessageSet(MessageC3Base):
    """C3 message set."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message set."""
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=ListTypes.X01,
        )
        self.zone1_power = False
        self.zone2_power = False
        self.dhw_power = False
        self.mode = 0
        self.zone_target_temp = [25.0, 25.0]
        self.dhw_target_temp = 40.0
        self.room_target_temp = 25.0
        self.zone1_curve = False
        self.zone2_curve = False
        self.fast_dhw = False
        self.tbh = False

    @property
    def _body(self) -> bytearray:
        # Byte 1
        zone1_power = 0x01 if self.zone1_power else 0x00
        zone2_power = 0x02 if self.zone2_power else 0x00
        dhw_power = 0x04 if self.dhw_power else 0x00
        # Byte 7
        zone1_curve = 0x01 if self.zone1_curve else 0x00
        zone2_curve = 0x02 if self.zone2_curve else 0x00
        tbh = 0x04 if self.tbh else 0x00
        fast_dhw = 0x08 if self.fast_dhw else 0x00
        room_target_temp = int(self.room_target_temp * 2)
        zone1_target_temp = int(self.zone_target_temp[0])
        zone2_target_temp = int(self.zone_target_temp[1])
        dhw_target_temp = int(self.dhw_target_temp)
        return bytearray(
            [
                zone1_power | zone2_power | dhw_power,
                self.mode,
                zone1_target_temp,
                zone2_target_temp,
                dhw_target_temp,
                room_target_temp,
                zone1_curve | zone2_curve | tbh | fast_dhw,
            ],
        )


class MessageSetSilent(MessageC3Base):
    """C3 message set silent."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message set silent."""
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=ListTypes.X05,
        )
        self.silent_mode = False
        self.silent_level = C3SilentLevel.OFF

    @property
    def _body(self) -> bytearray:
        return bytearray(
            [
                self.silent_level if self.silent_mode else C3SilentLevel.OFF,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ],
        )


class MessageSetECO(MessageC3Base):
    """C3 message set eco."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message set eco."""
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=ListTypes.X07,
        )
        self.eco_mode = False

    @property
    def _body(self) -> bytearray:
        eco_mode = 0x01 if self.eco_mode else 0

        return bytearray([eco_mode, 0x00, 0x00, 0x00, 0x00, 0x00])


class MessageSetDisinfect(MessageC3Base):
    """C3 message set Disinfect."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize C3 message set eco."""
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=ListTypes.X09,
        )
        self.disinfect = False

    @property
    def _body(self) -> bytearray:
        disinfect = 0x01 if self.disinfect else 0

        return bytearray([disinfect, 0x00, 0x00, 0x00])


class C3BasicBody(MessageBody):
    """C3 Basic message body."""

    def __init__(self, body: bytearray, data_offset: int = 0) -> None:
        """Initialize C3 message body."""
        super().__init__(body)
        # BodyBytes 1
        self.zone1_power = body[data_offset + 0] & 0x01 > 0
        self.zone2_power = body[data_offset + 0] & 0x02 > 0
        self.dhw_power = body[data_offset + 0] & 0x04 > 0
        self.zone1_curve = body[data_offset + 0] & 0x08 > 0
        self.zone2_curve = body[data_offset + 0] & 0x10 > 0
        self.tbh = body[data_offset + 0] & 0x20 > 0
        self.fast_dhw = body[data_offset + 0] & 0x40 > 0
        self.remote_onoff = body[data_offset + 0] & 0x80 > 0
        # BodyBytes 2
        self.heat = body[data_offset + 1] & 0x01 > 0
        self.cool = body[data_offset + 1] & 0x02 > 0
        self.dhw = body[data_offset + 1] & 0x04 > 0
        self.double_zone = body[data_offset + 1] & 0x08 > 0
        self.zone_temp_type = [
            body[data_offset + 1] & 0x10 > 0,
            body[data_offset + 1] & 0x20 > 0,
        ]
        self.room_thermal_support = body[data_offset + 1] & 0x40 > 0
        self.room_thermal_state = body[data_offset + 1] & 0x80 > 0
        # BodyBytes 3
        self.time_set = body[data_offset + 2] & 0x01 > 0
        self.silent_mode = body[data_offset + 2] & 0x02 > 0
        self.holiday_on = body[data_offset + 2] & 0x04 > 0
        self.eco_mode = body[data_offset + 2] & 0x08 > 0
        self.zone_terminal_type = body[data_offset + 2]
        # BodyBytes 4
        self.mode = body[data_offset + 3]
        self.mode_auto = body[data_offset + 4]
        # zone1, zone2
        self.zone_target_temp = [
            float(body[data_offset + 5]),
            float(body[data_offset + 6]),
        ]
        self.dhw_target_temp = float(body[data_offset + 7])
        self.room_target_temp = float(body[data_offset + 8] / 2)
        # zone1, zone2
        self.zone_heating_temp_max = [
            float(body[data_offset + 9]),
            float(body[data_offset + 13]),
        ]
        self.zone_heating_temp_min = [
            float(body[data_offset + 10]),
            float(body[data_offset + 14]),
        ]
        self.zone_cooling_temp_max = [
            float(body[data_offset + 11]),
            float(body[data_offset + 15]),
        ]
        self.zone_cooling_temp_min = [
            float(body[data_offset + 12]),
            float(body[data_offset + 16]),
        ]
        self.room_temp_max = float(body[data_offset + 17] / 2)
        self.room_temp_min = float(body[data_offset + 18] / 2)
        self.dhw_temp_max = float(body[data_offset + 19])
        self.dhw_temp_min = float(body[data_offset + 20])
        self.tank_actual_temperature = float(body[data_offset + 21])
        self.error_code = body[data_offset + 22]
        _code_info = C3_ERROR_CODE_TABLE.get(self.error_code)
        if self.error_code == 0:
            self.error_code_description = "No error"
        elif _code_info:
            self.error_code_description = f"{_code_info[0]}: {_code_info[1]}"
        else:
            self.error_code_description = f"Unknown code (raw={self.error_code})"
        self.tbh_control = body[data_offset + 23] & 0x80 > 0
        self.SysEnergyAnaEN = body[data_offset + 23] & 0x20 > 0
        self.HMIEnergyAnaSetEN = body[data_offset + 23] & 0x40 > 0
        # snake_case aliases so device attributes can be exposed under
        # canonical names via update_attributes_from_message()
        self.sys_energy_ana_en = self.SysEnergyAnaEN
        self.hmi_energy_ana_set_en = self.HMIEnergyAnaSetEN


class C3EnergyBody(MessageBody):
    """C3 Energy MSG_TYPE_UP_POWER4 message body."""

    def __init__(self, body: bytearray, data_offset: int = 0) -> None:
        """Initialize C3 notify1 message body."""
        super().__init__(body)
        status_byte = body[data_offset]
        # bit0
        self.status_heating = (status_byte & 0x01) > 0
        # bit1
        self.status_cool = (status_byte & 0x02) > 0
        # bit2
        self.status_dhw = (status_byte & 0x04) > 0
        # bit3
        self.status_tbh = (status_byte & 0x08) > 0
        # bit4
        self.status_ibh = (status_byte & 0x10) > 0
        # total_energy_consumption
        # Verified against wired-unit spreadsheet (2026-08-16):
        # total_electricity=14599 kWh appears as u16 BE at raw offset 4
        # (data_offset=1 → +3), NOT the u40 shift. Same for total_thermal.
        # Bytes 1-2 stayed 0 across all captures; the 40-bit shift produced
        # spurious ~9e8 readings.
        self.total_energy_consumption = (
            (body[data_offset + 3] << 8) + body[data_offset + 4]
        )
        # total_produced_energy (thermal counter, kWh) - u16 BE at offset 8
        self.total_produced_energy = (
            (body[data_offset + 7] << 8) + body[data_offset + 8]
        )
        base_value = body[data_offset + 9]
        self.outdoor_temperature = float(
            (base_value - 256) if base_value > TEMP_NEG_VALUE else base_value,
        )  # outdoor_temperature is t4
        self.zone1_temp_set = float(body[data_offset + 10])
        self.zone2_temp_set = float(body[data_offset + 11])
        self.t5s = body[data_offset + 12]
        self.tas = body[data_offset + 13]
        # WiFi module serial / model identifier is appended after the main
        # payload as an ASCII block preceded by a run of dash ("-") padding
        # bytes and terminated with NUL bytes. Layout observed on captured
        # frames: bytes ~96..159 = dashes, ~160..191 = ASCII serial, then NUL.
        # Search robustly (offsets may vary across firmware revisions).
        self.wifi_module_serial: str | None = None
        dash_run = b"-" * 20
        dash_idx = body.find(dash_run, data_offset)
        if dash_idx != -1:
            tail = body[dash_idx:]
            # skip the dash padding
            start = 0
            while start < len(tail) and tail[start:start + 1] == b"-":
                start += 1
            end = start
            while end < len(tail) and tail[end] != 0:
                end += 1
            candidate = bytes(tail[start:end]).strip()
            if candidate:
                try:
                    decoded = candidate.decode("ascii")
                except UnicodeDecodeError:
                    decoded = None
                if decoded and decoded.isprintable():
                    self.wifi_module_serial = decoded


class C3SilenceBody(MessageBody):
    """C3 Silence message body."""

    def __init__(self, body: bytearray, data_offset: int = 0) -> None:
        """Initialize C3 query silence message body."""
        super().__init__(body)
        self.silent_mode = body[data_offset] & 0x1 > 0
        self.silent_level = C3SilentLevel(
            (body[data_offset] & 0x1) + ((body[data_offset] & 0x8) >> 2)
            if self.silent_mode
            else C3SilentLevel.OFF.value,
        ).name
        # Message protocol information:
        # silence_function_state: Byte 1, BIT 0
        # silence_timer1_state: Byte 1, BIT 1
        # silence_timer2_state: Byte 1, BIT 2
        # silence_function_level: Byte 1, BIT 3
        # silence_timer1_starthour: Byte 2
        # silence_timer1_startmin: Byte 3
        # silence_timer1_endhour: Byte 4
        # silence_timer1_endmin: Byte 5
        # silence_timer2_starthour: Byte 6
        # silence_timer2_startmin: Byte 7
        # silence_timer2_endhour: Byte 8
        # silence_timer2_endmin: Byte 9


class C3ECOBody(MessageBody):
    """C3 ECO message body."""

    def __init__(self, body: bytearray, data_offset: int = 0) -> None:
        """Initialize C3 ECO message body."""
        super().__init__(body)
        self.eco_function_state = (
            len(body) > data_offset and body[data_offset] & ECO_FUNCTION_STATE_MASK > 0
        )
        self.eco_timer_state = (
            len(body) > data_offset and body[data_offset] & ECO_TIMER_STATE_MASK > 0
        )


class C3DisinfectBody(MessageBody):
    """C3 Disinfect message body."""

    def __init__(self, body: bytearray, data_offset: int = 0) -> None:
        """Initialize C3 Disinfect message body."""
        super().__init__(body)
        self.disinfect = body[data_offset] & 0x01 > 0
        self.disinfect_run = body[data_offset] & 0x02 > 0
        self.disinfect_set_weekday = body[data_offset + 1]
        self.disinfect_start_hour = body[data_offset + 2]
        self.disinfect_start_minutes = body[data_offset + 3]


class C3UnitParaBody(MessageBody):
    """C3 UnitPara message body."""

    def __init__(self, body: bytearray, data_offset: int = 0) -> None:
        """Initialize C3 UnitPara message body."""
        super().__init__(body)
        self.comp_run_freq = body[data_offset]
        _umr_raw = body[data_offset + 1]
        try:
            self.unit_mode_run = C3UnitRunMode(_umr_raw).name.lower()
        except ValueError:
            self.unit_mode_run = _umr_raw
        # NOTE: correlation vs wired HMI (Aug-16 pump test) shows fan RPM is
        # located at body[data_offset + 2] * 10 (not +3). Kept +3 as legacy
        # attribute name for backward compat.
        _fs_raw = body[data_offset + 2] * 10
        try:
            self.fan_speed = C3FanSpeed(_fs_raw).name.lower()
        except ValueError:
            self.fan_speed = _fs_raw
        self.fg_capacity_need = body[data_offset + 5]
        # Compressor current in A (verified against wired HMI Aug-16, raw=A)
        self.compressor_current = body[data_offset + 4]
        self.temp_t3 = body[data_offset + 6]
        self.temp_t4 = body[data_offset + 7]
        self.temp_tp = body[data_offset + 8]
        self.temp_tw_in = body[data_offset + 9]
        self.temp_tw_out = body[data_offset + 10]
        # Sensor sentinel: raw byte 127 (0x7F) is the C3 firmware convention
        # for "sensor not connected / not available". Convert to None so HA
        # can render the entity as unavailable instead of showing 127 °C.
        _tsolar = body[data_offset + 11]
        self.temp_tsolar = None if _tsolar == 127 else _tsolar
        self.hydbox_subtype = body[data_offset + 12]
        self.fg_usb_info_connect = body[data_offset + 13]
        # self.usb_index_max  body[data_offset + 14]
        # self.odu_comp_current  body[data_offset + 16]
        self.odu_voltage = body[data_offset + 17] * 256 + body[data_offset + 18]
        self.exv_current = body[data_offset + 19] * 256 + body[data_offset + 20]
        # canonical name matching Modbus documentation (EXV valve opening)
        self.exv_opening = self.exv_current
        self.odu_model = body[data_offset + 21]
        # self.unit_online_num  body[data_offset + 22]
        # self.current_code  body[data_offset + 23]
        self.temp_t1 = body[data_offset + 33]
        self.temp_tw2 = body[data_offset + 34]
        self.temp_t2 = body[data_offset + 35]
        self.temp_t2b = body[data_offset + 36]
        self.temp_t5 = body[data_offset + 37]
        self.temp_ta = body[data_offset + 38]
        # Buffer tank sensors: 127 = "sensor not connected" (verified against
        # user's installation with no buffer-tank probes wired).
        _tbt1 = body[data_offset + 39]
        _tbt2 = body[data_offset + 40]
        self.temp_tb_t1 = None if _tbt1 == 127 else _tbt1
        self.temp_tb_t2 = None if _tbt2 == 127 else _tbt2
        self.hydrobox_capacity = body[data_offset + 41]
        self.pressure_high = body[data_offset + 42] * 256 + body[data_offset + 43]
        self.pressure_low = body[data_offset + 44] * 256 + body[data_offset + 45]
        self.temp_th = body[data_offset + 46]
        # LOAD_OUTPUT bitmap at body[data_offset + 32] (data[33] in raw frame).
        # Bit-mapping validated against wired HMI (Aug-16 pump-run test):
        #   b2 = Backup heater (TBH)      -> load_output_tbh
        #   b3 = Water pump interior      -> pump_i
        #   b4 = SV1 (3-way DHW valve)    -> sv1
        #   b5 = SV2 (heating valve)      -> sv2
        #   b6 = Water pump outdoor       -> pump_o
        #   b7 = Water pump D             -> pump_d
        # b0/b1 (Pump_C, Pump_S, SV3, gas boiler) were never active in the
        # reference test; bit assignment for them is tentative.
        _load = body[data_offset + 32]
        self.load_output_raw   = _load
        self.pump_c_running    = bool(_load & 0x01)
        self.pump_s_running    = bool(_load & 0x02)
        self.load_output_tbh   = bool(_load & 0x04)
        self.pump_i_running    = bool(_load & 0x08)
        self.sv1_open          = bool(_load & 0x10)
        self.sv2_open          = bool(_load & 0x20)
        self.pump_o_running    = bool(_load & 0x40)
        self.pump_d_running    = bool(_load & 0x80)
        self.machine_type = body[data_offset + 47]
        self.odu_target_fre = body[data_offset + 48]
        # DC current in A. Correlation vs wired HMI (Aug-16 test):
        #   raw=3 -> 3 A ; raw=4 -> 4 A ; raw=5 -> 5 A. Unit is A (no scaling).
        self.dc_current = body[data_offset + 49]
        # DC-bus voltage in V. Correlation vs wired HMI: raw 33->330V, 37->370V.
        self.dc_bus_voltage = body[data_offset + 50] * 10
        self.temp_tf = body[data_offset + 51]
        self.idu_t1s1 = body[data_offset + 52]
        self.idu_t1s2 = body[data_offset + 53]
        # raw uint16 in 0.01 m3/h units -> divide by 100 for m3/h
        # (verified against wired HMI: raw 53 -> 0.53 m3/h)
        _wf_raw = body[data_offset + 54] * 256 + body[data_offset + 55]
        self.water_flow = _wf_raw / 100
        self.odu_plan_vol_lmt = body[data_offset + 56]
        # Instant power in kW (u16 BE /100). Correlation vs wired HMI (Aug-16):
        #   idle 0.00-2.13 kW ; run peak 4.24 kW. Overrides earlier X10-energy
        #   frozen sample at bytes 82..83 (that offset carries the last energy
        #   commit, not the instantaneous reading).
        self.instant_power = ((body[data_offset + 57] << 8) + body[data_offset + 58]) / 100
        # keep current_unit_capacity attribute (moved to a different offset if needed)
        # setting to None here as the previous mapping was incorrect.
        self.current_unit_capacity = None
        self.sphera_ahs_voltage = body[data_offset + 59]
        self.temp_t4a_ver = body[data_offset + 60]
        self.water_pressure = body[data_offset + 61] * 256 + body[data_offset + 62]
        self.room_rel_hum = body[data_offset + 63]
        # NOTE: pwm_pump_out removed - previous code shared offset 63 with
        # room_rel_hum which is clearly wrong. Actual offset unknown; entity
        # is unregistered until an authoritative source is available.
        # Verified against wired-unit spreadsheet (2026-08-16 09:57 snapshot):
        # total_electricity=14599 kWh at raw byte offset 69 → u16 BE at data_offset+68.
        # Values are 16-bit big-endian, unit = kWh. The previous 40-bit shift
        # produced spurious ~1.6e9 readings; correct decode is u16 BE.
        self.total_electricity0 = (
            (body[data_offset + 68] << 8) + body[data_offset + 69]
        )
        # total_thermal=10867 kWh at raw byte offset 73 → u16 BE at data_offset+72
        self.total_thermal0 = (
            (body[data_offset + 72] << 8) + body[data_offset + 73]
        )
        # heat_elec_total_consum=5834 kWh at raw byte offset 77 → data_offset+76
        self.heat_elec_total_consum0 = (
            (body[data_offset + 76] << 8) + body[data_offset + 77]
        )
        # heat_elec_total_capacity mirrors thermal (10867 kWh) at data_offset+80
        self.heat_elec_total_capacity0 = (
            (body[data_offset + 80] << 8) + body[data_offset + 81]
        )
        # raw uint16 in 0.01 kW units -> divide by 100 for kW
        # (verified against wired HMI: raw 209 -> 2.09 kW)
        self.instant_power0 = ((body[data_offset + 82] << 8) + body[data_offset + 83]) / 100
        # scaled to kW (0.01 kW units) for consistency with instant_power0
        self.instant_renew_power0 = ((body[data_offset + 84] << 8) + body[data_offset + 85]) / 100
        # TODO: previous version aliased this to instant_renew_power0 bytes.
        # Best-effort correction: use the next uint16 at offset 86-87.
        # Confirm against wired HMI once a non-zero PV production sample exists.
        self.total_renew_power0 = ((body[data_offset + 86] << 8) + body[data_offset + 87]) / 100
        # ------------------------------------------------------------------
        # IDU / ODU software versions (Modbus reg 130 / reg 1042 mapped
        # into X10 telemetry frame). Verified against wired HMI:
        #   raw byte offset 94 = IDU sw version = 14  (HMI shows "V14")
        #   raw byte offset 95 = ODU sw version = 64  (HMI shows "V64")
        # HMI software version ("V56A" on wired display) is NOT present in
        # X10 / X04 / long-X05 payloads - the C3 telemetry frames only
        # expose IDU + ODU firmware. Left unimplemented until an
        # authoritative source is available.
        self.idu_software_version = body[data_offset + 93]
        self.odu_software_version = body[data_offset + 94]
        # ------------------------------------------------------------------
        # WiFi module serial: appended as ASCII after a run of "-" padding.
        # Verified: bytes 160..191 = "0000C3310171H120F24114100123MNJ2".
        self.wifi_module_serial: str | None = None
        dash_run = b"-" * 20
        dash_idx = body.find(dash_run, data_offset)
        if dash_idx != -1:
            tail = body[dash_idx:]
            start = 0
            while start < len(tail) and tail[start:start + 1] == b"-":
                start += 1
            end = start
            while end < len(tail) and tail[end] != 0:
                end += 1
            candidate = bytes(tail[start:end]).strip()
            if candidate:
                try:
                    decoded = candidate.decode("ascii")
                except UnicodeDecodeError:
                    decoded = None
                if decoded and decoded.isprintable():
                    self.wifi_module_serial = decoded



class C3UnitParaExtBody(MessageBody):
    """C3 extended UnitPara/runtime notification body.

    Sent asynchronously by the device (notify1 + body_type X05, 239 B).
    Overlaps with X10 for most telemetry (temps, pressures, instant power,
    total electricity/thermal counters) - those fields are intentionally
    NOT re-exposed to avoid duplicate entities. Only fields unique to
    this frame are parsed here.

    Layout verified against wired HMI (Galmet Prima 06 GT, 2026-08-16 log):
    - offset 57-58 (u16 BE): compressor total run time in hours (2356 h)
    - other counters at 50, 55-56, 59-60 are candidates for future
      decoding (need more samples over time).
    """

    def __init__(self, body: bytearray, data_offset: int = 0) -> None:
        """Initialize C3 UnitParaExt (long X05 notify) message body."""
        super().__init__(body)
        # Compressor total run time (hours). Verified against wired HMI.
        # data_offset=1 skips body_type; absolute frame offsets are 57-58,
        # so relative to data_offset we read + 56 and + 57.
        self.comp_total_run_time = (
            body[data_offset + 56] * 256 + body[data_offset + 57]
        )


class MessageC3Response(MessageResponse):
    """C3 message response."""

    def __init__(self, message: bytes) -> None:
        """Initialize C3 message response."""
        super().__init__(bytearray(message))
        if (
            self.message_type
            in [MessageType.set, MessageType.notify1, MessageType.query]
            and self.body_type == ListTypes.X01
        ) or self.message_type == MessageType.notify2:
            self.set_body(C3BasicBody(super().body, data_offset=1))
        elif (
            self.message_type == MessageType.notify1 and self.body_type == ListTypes.X04
        ):
            self.set_body(C3EnergyBody(super().body, data_offset=1))
        elif (
            self.message_type == MessageType.notify1
            and self.body_type == ListTypes.X05
        ):
            # Long (239 B) notify1 frame with extra runtime counters.
            self.set_body(C3UnitParaExtBody(super().body, data_offset=1))
        elif self.message_type == MessageType.query and self.body_type == ListTypes.X05:
            self.set_body(C3SilenceBody(super().body, data_offset=1))
        elif self.body_type == ListTypes.X07:
            self.set_body(C3ECOBody(super().body, data_offset=1))
        elif self.body_type == ListTypes.X09:
            self.set_body(C3DisinfectBody(super().body, data_offset=1))
        elif self.body_type == ListTypes.X10:
            self.set_body(C3UnitParaBody(super().body, data_offset=1))
        self.set_attr()
