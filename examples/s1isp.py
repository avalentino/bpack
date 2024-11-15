"""Sentinel-1 Instrument Source Packets (ISP) decoding example."""

import enum
import logging
import datetime

import bpack
import bpack.bs
from bpack import T

BITS = bpack.EBaseUnits.BITS
BE = bpack.EByteOrder.BE


SYNK_MARKER = 0x352EF853
FREF = 37.53472224


class SyncMarkerException(RuntimeError):
    pass


class EEccNumber(enum.IntEnum):
    # TODO: check "NOT_SET"
    NOT_SET = 0  # CONTINGENCY: RESERVED FOR GROUND TESTING OR MODE UPGRADING
    S1 = 1
    S2 = 2
    S3 = 3
    S4 = 4
    S5_N = 5
    S6 = 6
    IW = 8
    WM = 9
    S5_S = 10
    S1_NO_ICAL = 11
    S2_NO_ICAL = 12
    S3_NO_ICAL = 13
    S4_NO_ICAL = 14
    RFC = 15
    TEST = 16
    EN_S3 = 17
    AN_S1 = 18
    AN_S2 = 19
    AN_S3 = 20
    AN_S4 = 21
    AN_S5_N = 22
    AN_S5_S = 23
    AN_S6 = 24
    S5_N_NO_ICAL = 25
    S5_S_NO_ICAL = 26
    S6_NO_ICAL = 27
    EN_S3_NO_ICAL = 31
    EN = 32
    AN_S1_NO_ICAL = 33
    AN_S3_NO_ICAL = 34
    AN_S6_NO_ICAL = 35
    NC_S1 = 37
    NC_S2 = 38
    NC_S3 = 39
    NC_S4 = 40
    NC_S5_N = 41
    NC_S5_S = 42
    NC_S6 = 43
    NC_EW = 44
    NC_IW = 45
    NC_WM = 46


class ETestMode(enum.IntEnum):
    DEFAULT = 0
    CONTINGENCY_RXM_FULLY_OPERATIONAL = 4  # 100
    CONTINGENCY_RXM_FULLY_BYPASSED = 5  # 101
    OPER = 6  # 110
    BYPASS = 7  # 111


class ERxChannelId(enum.IntEnum):
    V = 0
    H = 1


class EBaqMode(enum.IntEnum):
    BYPASS = 0
    BAQ3 = 3
    BAQ4 = 4
    BAQ5 = 5
    FDBAQ_MODE_0 = 12
    FDBAQ_MODE_1 = 13
    FDBAQ_MODE_2 = 14


class ERangeDecimation(enum.IntEnum):
    X3_ON_4 = 0
    X2_ON_3 = 1
    X5_ON_9 = 3
    X4_ON_9 = 4
    X3_ON_8 = 5
    X1_ON_3 = 6
    X1_ON_6 = 7
    X3_ON_7 = 8
    X5_ON_16 = 9
    X3_ON_26 = 10
    X4_ON_11 = 11


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class PacketPrimaryHeader:
    version: T["u3"] = 0
    packet_type: T["u1"] = 0
    secondary_header_flag: bool = True
    pid: T["u7"] = 0
    pcat: T["u4"] = 0
    sequence_flags: T["u2"] = 0
    sequence_counter: T["u14"] = 0
    packet_data_length: T["u16"] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class DatationService:
    coarse_time: T["u32"] = 0
    fine_time: T["u16"] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class FixedAncillaryDataService:
    sync_marker: T["u32"] = SYNK_MARKER
    data_take_id: T["u32"] = 0
    ecc_num: EEccNumber = bpack.field(size=8, default=EEccNumber.NOT_SET)
    # n. 1 bit n/a
    test_mode: ETestMode = bpack.field(
        size=3, offset=73, default=ETestMode.DEFAULT
    )
    rx_channel_id: ERxChannelId = bpack.field(size=4, default=ERxChannelId.V)
    instrument_configuration_id: T["u32"] = 0  # NOTE: the data type is TBD


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class SubCommunicationAncillaryDataService:
    word_index: T["u8"] = 0
    word_data: T["u16"] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class CounterService:
    space_packet_count: T["u32"] = 0
    pri_count: T["u32"] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class RadarConfigurationSupportService:
    error_flag: bool = False
    baq_mode: EBaqMode = bpack.field(size=5, offset=3, default=EBaqMode.BYPASS)
    baq_block_len: T["u8"] = 0
    # n. 8 bits padding
    range_decimation: ERangeDecimation = bpack.field(
        size=8, offset=24, default=0
    )
    rx_gain: T["u8"] = 0
    tx_ramp_rate: T["u16"] = 0
    tx_pulse_start_freq: T["u16"] = 0
    tx_pulse_length: T["u24"] = 0
    # n. 3 bits pad
    rank: T["u5"] = bpack.field(offset=99, default=0)
    pri: T["u24"] = 0
    swst: T["u24"] = 0
    swl: T["u24"] = 0
    sas_sbb_message: T["S24"] = 0  # TODO: replace with SAS sub-record
    ses_sbb_message: T["S24"] = 0  # TODO: replace with SES sub-record


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE, size=24)
class RadarSampleCountService:
    number_of_quads: T["u16"] = 0
    # n. 8 bits pad


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class PacketSecondaryHeader:
    datation_service: DatationService
    fixed_ancillary_data_service: FixedAncillaryDataService
    subcom_ancillary_data_service: SubCommunicationAncillaryDataService
    counters_service: CounterService
    radar_configuration_support_service: RadarConfigurationSupportService
    radar_sample_count_service: RadarSampleCountService


def sequential_stream_decoder(filename, maxcount=None):
    """Decode packet headers and store them into a pandas data-frame."""
    import tqdm
    import pandas as pd

    log = logging.getLogger(__name__)
    log.info(f'start decoding: "{filename}"')
    t0 = datetime.datetime.now()

    primary_header_size = bpack.calcsize(
        PacketPrimaryHeader, bpack.EBaseUnits.BYTES
    )
    secondary_header_size = bpack.calcsize(
        PacketSecondaryHeader, bpack.EBaseUnits.BYTES
    )
    records = []
    packet_counter = 0
    pbar = tqdm.tqdm(unit=" packets", desc="decoded")
    with open(filename, "rb") as fd, pbar:
        while fd:
            # primary header
            data = fd.read(primary_header_size)
            if len(data) == 0 or (maxcount and len(records) > maxcount):
                break

            # type - PacketPrimaryHeader
            primary_header = PacketPrimaryHeader.frombytes(data)
            # print(primary_header)

            assert primary_header.version == 0
            assert primary_header.packet_type == 0
            assert primary_header.sequence_flags == 3
            # assert primary_header.sequence_counter == packet_counter % 2**14

            # secondary header
            assert primary_header.secondary_header_flag
            data_field_size = primary_header.packet_data_length + 1
            data = fd.read(data_field_size)

            # type - PacketSecondaryHeader
            secondary_header = PacketSecondaryHeader.frombytes(
                data[:secondary_header_size]
            )
            # print(secondary_header)

            sync = secondary_header.fixed_ancillary_data_service.sync_marker
            if sync != SYNK_MARKER:
                raise SyncMarkerException(
                    f"packat count: {packet_counter + 1}"
                )

            radar_cfg = secondary_header.radar_configuration_support_service
            assert radar_cfg.error_flag is False
            # baq_block_len = 8 * (radar_cfg.baq_block_len + 1)
            # assert baq_block_len == 256, (
            #     f'baq_block_len: {radar_cfg.baq_block_len}, '
            #     f'baq_mode: {radar_cfg.baq_mode}'
            # )

            counters_service = secondary_header.counters_service
            assert packet_counter == counters_service.space_packet_count
            packet_counter += 1

            # update the dataframe
            r = bpack.asdict(primary_header)
            r.update(bpack.asdict(secondary_header.datation_service))
            r.update(
                bpack.asdict(secondary_header.fixed_ancillary_data_service)
            )
            r.update(
                bpack.asdict(secondary_header.subcom_ancillary_data_service)
            )
            r.update(bpack.asdict(secondary_header.counters_service))
            r.update(
                bpack.asdict(
                    secondary_header.radar_configuration_support_service
                )
            )
            r.update(bpack.asdict(secondary_header.radar_sample_count_service))
            records.append(r)

            # user data
            # TBW

            pbar.update()

    elapsed = datetime.datetime.now() - t0
    log.info(f"decoding complete (elapsed time: {elapsed})")

    return pd.DataFrame(records)


if __name__ == "__main__":
    import os
    import sys

    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s"
    )

    filename = (
        "S1B_S3_RAW__0SDV_20210530T130904_20210530T130929_027134_033DC1_1AF2.SAFE/"
        "s1b-s3-raw-s-vv-20210530t130904-20210530t130929-027134-033dc1.dat"
    )
    if not os.path.exists(filename):
        sys.exit(
            """ERROR: sample product not available.

You can download it as follows (scihub.copernicus.eu authentication needed):

$ sentinelsat --name 'S1B_S3_RAW__0SDV_20200615T162409_20200615T162435_022046_029D76*' --download
"""
        )

    df = sequential_stream_decoder(filename)  # , maxcount=10)
    # print()
    # print(df.head())

"""
$ env PYTHONPATH=.. python3 s1isp.py
2021-06-03 08:56:31,783 INFO: start decoding: "S1B_S3_RAW__0SDV_20210530T130904_20210530T130929_027134_033DC1_1AF2.SAFE/s1b-s3-raw-s-vv-20210530t130904-20210530t130929-027134-033dc1.dat"
decoded: 48941 packets [00:19, 2506.83 packets/s]
2021-06-03 08:56:51,320 INFO: decoding complete (elapsed time: 0:00:19.537022)
"""
