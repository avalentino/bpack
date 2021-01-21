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
    # TODO: check "not_set"
    not_set = 0  # contingency: reserved for ground testing or mode upgrading
    s1 = 1
    s2 = 2
    s3 = 3
    s4 = 4
    s5_n = 5
    s6 = 6
    iw = 8
    wm = 9
    s5_s = 10
    s1_no_ical = 11
    s2_no_ical = 12
    s3_no_ical = 13
    s4_no_ical = 14
    rfc = 15
    test = 16
    en_s3 = 17
    an_s1 = 18
    an_s2 = 19
    an_s3 = 20
    an_s4 = 21
    an_s5_n = 22
    an_s5_s = 23
    an_s6 = 24
    s5_n_no_ical = 25
    s5_s_no_ical = 26
    s6_no_ical = 27
    en_s3_no_ical = 31
    en = 32
    an_s1_no_ical = 33
    an_s3_no_ical = 34
    an_s6_no_ical = 35
    nc_s1 = 37
    nc_s2 = 38
    nc_s3 = 39
    nc_s4 = 40
    nc_s5_n = 41
    nc_s5_s = 42
    nc_s6 = 43
    nc_ew = 44
    nc_iw = 45
    nc_wm = 46


class ETestMode(enum.IntEnum):
    default = 0
    contingency_rxm_fully_operational = 4   # 100
    contingency_rxm_fully_bypassed = 5      # 101
    oper = 6                                # 110
    bypass = 7                              # 111


class ERxChannelId(enum.IntEnum):
    V = 0
    H = 1


class EBaqMode(enum.IntEnum):
    bypass = 0
    baq3 = 3
    baq4 = 4
    baq5 = 5
    fdbaq_mode_0 = 12
    fdbaq_mode_1 = 13
    fdbaq_mode_2 = 14


class ERangeDecimation(enum.IntEnum):
    x3_on_4 = 0
    x2_on_3 = 1
    x5_on_9 = 3
    x4_on_9 = 4
    x3_on_8 = 5
    x1_on_3 = 6
    x1_on_6 = 7
    x3_on_7 = 8
    x5_on_16 = 9
    x3_on_26 = 10
    x4_on_11 = 11


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class PacketPrimaryHeader:
    version: T['u3'] = 0
    packet_type: T['u1'] = 0
    secondary_header_flag: bool = True
    pid: T['u7'] = 0
    pcat: T['u4'] = 0
    sequence_flags: T['u2'] = 0
    sequence_counter: T['u14'] = 0
    packet_data_length: T['u16'] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class DatationService:
    coarse_time: T['u32'] = 0
    fine_time: T['u16'] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class FixedAncillaryDataService:
    sync_marker: T['u32'] = SYNK_MARKER
    data_take_id: T['u32'] = 0
    ecc_num: EEccNumber = bpack.field(size=8, default=EEccNumber.not_set)
    # n. 1 bit n/a
    test_mode: ETestMode = bpack.field(size=3, offset=73,
                                       default=ETestMode.default)
    rx_channel_id: ERxChannelId = bpack.field(size=4, default=ERxChannelId.V)
    instrument_configuration_id: T['u32'] = 0  # NOTE: the data type is TBD


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class SubCommunicationAncillaryDataService:
    word_index: T['u8'] = 0
    word_data: T['u16'] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class CounterService:
    space_packet_count: T['u32'] = 0
    pri_count: T['u32'] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class RadarConfigurationSupportService:
    error_flag: bool = False
    baq_mode: EBaqMode = bpack.field(size=5, offset=3, default=EBaqMode.bypass)
    baq_block_len: T['u8'] = 0
    # n. 8 bits padding
    range_decimation: ERangeDecimation = bpack.field(size=8, offset=24,
                                                     default=0)
    rx_gain: T['u8'] = 0
    tx_ramp_rate: T['u16'] = 0
    tx_pulse_start_freq: T['u16'] = 0
    tx_pulse_length: T['u24'] = 0
    # n. 3 bits pad
    rank: T['u5'] = bpack.field(offset=99, default=0)
    pri: T['u24'] = 0
    swst: T['u24'] = 0
    swl: T['u24'] = 0
    sas_sbb_message: T['S24'] = 0       # TODO: replace with SAS sub-record
    ses_sbb_message: T['S24'] = 0       # TODO: replace with SES sub-record


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE, size=24)
class RadarSampleCountService:
    number_of_quads: T['u16'] = 0
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

    primary_header_size = bpack.calcsize(PacketPrimaryHeader,
                                         bpack.EBaseUnits.BYTES)
    secondary_header_size = bpack.calcsize(PacketSecondaryHeader,
                                           bpack.EBaseUnits.BYTES)
    records = []
    packet_counter = 0
    pbar = tqdm.tqdm(unit=' packets', desc='decoded')
    with open(filename, 'rb') as fd, pbar:
        while fd:
            # primary header
            data = fd.read(primary_header_size)
            if len(data) == 0 or (maxcount and len(records) > maxcount):
                break

            # type: PacketPrimaryHeader
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

            # type: PacketSecondaryHeader
            secondary_header = PacketSecondaryHeader.frombytes(
                data[:secondary_header_size])
            # print(secondary_header)

            sync = secondary_header.fixed_ancillary_data_service.sync_marker
            if sync != SYNK_MARKER:
                raise SyncMarkerException(
                    f'packat count: {packet_counter + 1}')

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
            r.update(bpack.asdict(
                secondary_header.fixed_ancillary_data_service))
            r.update(bpack.asdict(
                secondary_header.subcom_ancillary_data_service))
            r.update(bpack.asdict(secondary_header.counters_service))
            r.update(bpack.asdict(
                secondary_header.radar_configuration_support_service))
            r.update(bpack.asdict(secondary_header.radar_sample_count_service))
            records.append(r)

            # user data
            # TBW

            pbar.update()

    elapsed = datetime.datetime.now() - t0
    log.info(f'decoding complete (elapsed time: {elapsed})')

    return pd.DataFrame(records)


if __name__ == '__main__':
    import os
    import sys

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s')

    filename = (
        'S1B_S3_RAW__0SDV_20200615T162409_20200615T162435_022046_029D76_F3E6.SAFE/'
        's1b-s3-raw-s-vv-20200615t162409-20200615t162435-022046-029d76.dat'
    )
    if not os.path.exists(filename):
        sys.exit("""ERROR: sample product not available.

You can download it as follows (scihub.copernicus.eu authentication needed):

$ sentinelsat --name 'S1B_S3_RAW__0SDV_20200615T162409_20200615T162435_022046_029D76*' --download
""")

    df = sequential_stream_decoder(filename)  # , maxcount=10)
    # print()
    # print(df.head())
