#include "edge/config.h"
#include "edge/journal.h"
#include "edge/modbus.h"
#include "edge/modbus_crc.h"
#include "edge/point.h"
#include "edge/queue.h"
#include "edge/scheduler.h"
#include "edge/state_machine.h"
#include "edge/telemetry.h"
#include "edge/update_manifest.h"

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

static edge_point_record_t make_point(uint64_t sequence)
{
    edge_point_record_t point = {0};
    const int written = snprintf(
        point.point_id,
        sizeof(point.point_id),
        "test.point.%llu",
        (unsigned long long)sequence
    );

    assert(written > 0);
    assert((size_t)written < sizeof(point.point_id));
    point.sequence = sequence;
    point.monotonic_ms = sequence * 10U;
    point.value_type = EDGE_VALUE_U64;
    point.value.u64 = sequence;
    point.quality = EDGE_QUALITY_GOOD;
    (void)strcpy(point.unit, "count");
    (void)strcpy(point.source, "test");
    point.config_revision = 1U;
    return point;
}

static void test_identifier_validation(void)
{
    char missing_terminator[EDGE_POINT_ID_CAPACITY];

    (void)memset(missing_terminator, 'a', sizeof(missing_terminator));
    assert(edge_point_identifier_is_valid("tank.level-1", 49U));
    assert(!edge_point_identifier_is_valid("", 49U));
    assert(!edge_point_identifier_is_valid("tank/level", 49U));
    assert(!edge_point_identifier_is_valid(missing_terminator, sizeof(missing_terminator)));
    assert(!edge_point_identifier_is_valid(NULL, 49U));
}

static void test_quality(void)
{
    edge_point_record_t point = make_point(1U);

    assert(edge_point_is_good(&point));
    edge_point_add_quality(&point, EDGE_QUALITY_COMM_TIMEOUT);
    edge_point_add_quality(&point, EDGE_QUALITY_STALE);
    assert(!edge_point_is_good(&point));
    assert(edge_point_has_quality(&point, EDGE_QUALITY_COMM_TIMEOUT));
    assert(edge_point_has_quality(&point, EDGE_QUALITY_STALE));
    edge_point_clear_quality(&point, EDGE_QUALITY_COMM_TIMEOUT);
    assert(!edge_point_has_quality(&point, EDGE_QUALITY_COMM_TIMEOUT));
    assert(edge_point_has_quality(&point, EDGE_QUALITY_STALE));
}

static void test_queue_reject_new(void)
{
    edge_point_record_t storage[2];
    edge_point_record_t output;
    edge_queue_t queue;
    edge_point_record_t point1 = make_point(1U);
    edge_point_record_t point2 = make_point(2U);
    edge_point_record_t point3 = make_point(3U);

    assert(edge_queue_init(&queue, storage, 2U, EDGE_QUEUE_REJECT_NEW) == EDGE_QUEUE_OK);
    assert(edge_queue_is_empty(&queue));
    assert(edge_queue_push(&queue, &point1) == EDGE_QUEUE_OK);
    assert(edge_queue_push(&queue, &point2) == EDGE_QUEUE_OK);
    assert(edge_queue_is_full(&queue));
    assert(edge_queue_push(&queue, &point3) == EDGE_QUEUE_FULL);
    assert(queue.dropped_total == 0U);
    assert(edge_queue_pop(&queue, &output) == EDGE_QUEUE_OK);
    assert(output.sequence == 1U);
    assert(edge_queue_pop(&queue, &output) == EDGE_QUEUE_OK);
    assert(output.sequence == 2U);
    assert(edge_queue_pop(&queue, &output) == EDGE_QUEUE_EMPTY);
}

static void test_queue_drop_oldest_and_wrap(void)
{
    edge_point_record_t storage[3];
    edge_point_record_t output;
    edge_queue_t queue;
    uint64_t sequence = 0U;

    assert(edge_queue_init(&queue, storage, 3U, EDGE_QUEUE_DROP_OLDEST) == EDGE_QUEUE_OK);
    for (sequence = 1U; sequence <= 5U; ++sequence) {
        edge_point_record_t point = make_point(sequence);
        assert(edge_queue_push(&queue, &point) == EDGE_QUEUE_OK);
    }

    assert(edge_queue_count(&queue) == 3U);
    assert(queue.pushed_total == 5U);
    assert(queue.dropped_total == 2U);

    for (sequence = 3U; sequence <= 5U; ++sequence) {
        assert(edge_queue_pop(&queue, &output) == EDGE_QUEUE_OK);
        assert(output.sequence == sequence);
    }
    assert(queue.popped_total == 3U);
}

static void test_queue_invalid_arguments(void)
{
    edge_point_record_t storage[1];
    edge_queue_t queue;

    assert(edge_queue_init(NULL, storage, 1U, EDGE_QUEUE_REJECT_NEW) == EDGE_QUEUE_INVALID_ARGUMENT);
    assert(edge_queue_init(&queue, NULL, 1U, EDGE_QUEUE_REJECT_NEW) == EDGE_QUEUE_INVALID_ARGUMENT);
    assert(edge_queue_init(&queue, storage, 0U, EDGE_QUEUE_REJECT_NEW) == EDGE_QUEUE_INVALID_ARGUMENT);
}

static void test_modbus_crc(void)
{
    static const uint8_t request[] = {
        UINT8_C(0x01),
        UINT8_C(0x03),
        UINT8_C(0x00),
        UINT8_C(0x00),
        UINT8_C(0x00),
        UINT8_C(0x0A)
    };

    assert(edge_modbus_crc16(request, sizeof(request)) == UINT16_C(0xCDC5));
    assert(edge_modbus_crc16(NULL, 1U) == 0U);
}

static void test_modbus_frames_and_decoding(void)
{
    uint8_t request[EDGE_MODBUS_REQUEST_SIZE];
    uint8_t response[] = {
        UINT8_C(0x11),
        UINT8_C(0x03),
        UINT8_C(0x04),
        UINT8_C(0x3F),
        UINT8_C(0x80),
        UINT8_C(0x00),
        UINT8_C(0x00),
        0U,
        0U
    };
    size_t request_length = 0U;
    edge_modbus_response_t parsed = {NULL, 0U, 0U};
    uint16_t crc = 0U;
    uint32_t integer = 0U;
    float floating = 0.0F;

    assert(
        edge_modbus_build_read_request(
            UINT8_C(0x11),
            UINT8_C(0x03),
            UINT16_C(0x006B),
            UINT16_C(0x0002),
            request,
            sizeof(request),
            &request_length
        ) == EDGE_MODBUS_OK
    );
    assert(request_length == sizeof(request));
    assert(request[0] == UINT8_C(0x11));
    assert(request[2] == UINT8_C(0x00));
    assert(request[3] == UINT8_C(0x6B));

    crc = edge_modbus_crc16(response, sizeof(response) - 2U);
    response[sizeof(response) - 2U] =
        (uint8_t)(crc & UINT16_C(0x00FF));
    response[sizeof(response) - 1U] = (uint8_t)(crc >> 8U);
    assert(
        edge_modbus_parse_read_response(
            response,
            sizeof(response),
            UINT8_C(0x11),
            UINT8_C(0x03),
            &parsed
        ) == EDGE_MODBUS_OK
    );
    assert(parsed.data_length == 4U);
    assert(
        edge_modbus_decode_u32(
            parsed.data,
            parsed.data_length,
            EDGE_MODBUS_ORDER_ABCD,
            &integer
        ) == EDGE_MODBUS_OK
    );
    assert(integer == UINT32_C(0x3F800000));
    assert(
        edge_modbus_decode_f32(
            parsed.data,
            parsed.data_length,
            EDGE_MODBUS_ORDER_ABCD,
            &floating
        ) == EDGE_MODBUS_OK
    );
    assert(floating == 1.0F);
    response[4] ^= UINT8_C(0x01);
    assert(
        edge_modbus_parse_read_response(
            response,
            sizeof(response),
            UINT8_C(0x11),
            UINT8_C(0x03),
            &parsed
        ) == EDGE_MODBUS_CRC_ERROR
    );
}

static void test_configuration_validation(void)
{
    edge_modbus_device_config_t devices[1] = {0};
    edge_point_config_t points[2] = {0};
    edge_config_error_t error = {EDGE_CONFIG_OK, 0U, NULL};
    edge_runtime_config_t config = {
        UINT32_C(7),
        devices,
        1U,
        points,
        2U
    };

    (void)strcpy(devices[0].id, "meter-1");
    devices[0].port = EDGE_CONFIG_PORT_RS485_A;
    devices[0].slave = UINT8_C(11);
    devices[0].baud = UINT32_C(19200);
    devices[0].parity = EDGE_CONFIG_PARITY_EVEN;
    devices[0].timeout_ms = UINT32_C(300);
    devices[0].retries = UINT8_C(2);

    (void)strcpy(points[0].id, "meter.power");
    points[0].source = EDGE_CONFIG_SOURCE_MODBUS;
    points[0].period_ms = UINT32_C(1000);
    points[0].stale_ms = UINT32_C(5000);
    points[0].modbus_device_index = UINT8_C(0);
    points[0].modbus_function = UINT8_C(3);
    points[0].modbus_quantity = UINT16_C(2);

    (void)strcpy(points[1].id, "panel.door");
    points[1].source = EDGE_CONFIG_SOURCE_DIGITAL;
    points[1].period_ms = UINT32_C(50);
    points[1].stale_ms = UINT32_C(500);
    points[1].channel = UINT8_C(1);

    assert(edge_config_validate(&config, &error) == EDGE_CONFIG_OK);
    (void)strcpy(points[1].id, "meter.power");
    assert(
        edge_config_validate(&config, &error)
        == EDGE_CONFIG_DUPLICATE_IDENTIFIER
    );
    assert(error.index == 1U);
    (void)strcpy(points[1].id, "panel.door");
    points[0].modbus_device_index = UINT8_C(1);
    assert(
        edge_config_validate(&config, &error)
        == EDGE_CONFIG_INVALID_REFERENCE
    );
}

static void test_scheduler_backoff(void)
{
    edge_schedule_t schedule = {0U, 0U, 0U, 0U};

    assert(edge_schedule_init(
        &schedule,
        UINT32_C(100),
        UINT32_C(800),
        UINT64_C(1000),
        UINT32_C(25)
    ));
    assert(!edge_schedule_is_due(&schedule, UINT64_C(1024)));
    assert(edge_schedule_is_due(&schedule, UINT64_C(1025)));
    edge_schedule_complete(&schedule, UINT64_C(1025), false);
    assert(schedule.next_due_ms == UINT64_C(1225));
    edge_schedule_complete(&schedule, UINT64_C(1225), false);
    assert(schedule.next_due_ms == UINT64_C(1625));
    edge_schedule_complete(&schedule, UINT64_C(1625), false);
    assert(schedule.next_due_ms == UINT64_C(2425));
    edge_schedule_complete(&schedule, UINT64_C(2425), true);
    assert(schedule.next_due_ms == UINT64_C(2525));
    assert(schedule.consecutive_failures == 0U);
}

static void test_journal_recovery(void)
{
    static const uint8_t first[] = {
        UINT8_C(0x10),
        UINT8_C(0x20),
        UINT8_C(0x30)
    };
    static const uint8_t second[] = {
        UINT8_C(0x40),
        UINT8_C(0x50)
    };
    uint8_t storage[128] = {0U};
    size_t first_length = 0U;
    size_t second_length = 0U;
    edge_journal_scan_t scan;
    edge_journal_record_t record = {0U, NULL, 0U, 0U};

    assert(
        edge_journal_encode(
            UINT64_C(41),
            first,
            (uint32_t)sizeof(first),
            storage,
            sizeof(storage),
            &first_length
        ) == EDGE_JOURNAL_OK
    );
    assert(
        edge_journal_encode(
            UINT64_C(42),
            second,
            (uint32_t)sizeof(second),
            &storage[first_length],
            sizeof(storage) - first_length,
            &second_length
        ) == EDGE_JOURNAL_OK
    );
    scan = edge_journal_scan(storage, first_length + second_length);
    assert(scan.stop_reason == EDGE_JOURNAL_OK);
    assert(scan.record_count == 2U);
    assert(scan.last_sequence == UINT64_C(42));
    assert(
        edge_journal_decode(storage, first_length, &record)
        == EDGE_JOURNAL_OK
    );
    assert(record.payload_length == sizeof(first));
    assert(memcmp(record.payload, first, sizeof(first)) == 0);

    scan = edge_journal_scan(
        storage,
        first_length + second_length - 1U
    );
    assert(scan.record_count == 1U);
    assert(scan.valid_bytes == first_length);
    assert(scan.stop_reason == EDGE_JOURNAL_TORN_WRITE);
    storage[EDGE_JOURNAL_HEADER_SIZE] ^= UINT8_C(0x01);
    scan = edge_journal_scan(storage, first_length + second_length);
    assert(scan.record_count == 0U);
    assert(scan.stop_reason == EDGE_JOURNAL_CORRUPT);
}

static void test_state_machine(void)
{
    edge_state_machine_t machine;

    edge_state_machine_init(&machine);
    assert(machine.state == EDGE_STATE_BOOT);
    assert(edge_state_machine_dispatch(
        &machine,
        EDGE_EVENT_BOOT_COMPLETE
    ));
    assert(edge_state_machine_dispatch(
        &machine,
        EDGE_EVENT_SELF_TEST_OK
    ));
    assert(edge_state_machine_dispatch(
        &machine,
        EDGE_EVENT_CONFIG_AVAILABLE
    ));
    assert(edge_state_machine_dispatch(
        &machine,
        EDGE_EVENT_NETWORK_READY
    ));
    assert(machine.state == EDGE_STATE_RUNNING);
    assert(edge_state_machine_dispatch(
        &machine,
        EDGE_EVENT_NETWORK_LOST
    ));
    assert(machine.state == EDGE_STATE_DEGRADED);
    assert(edge_state_machine_dispatch(
        &machine,
        EDGE_EVENT_UPDATE_REQUESTED
    ));
    assert(machine.state == EDGE_STATE_UPDATING);
    assert(edge_state_machine_dispatch(
        &machine,
        EDGE_EVENT_UPDATE_FAILED
    ));
    assert(machine.state == EDGE_STATE_DEGRADED);
    assert(strcmp(edge_state_name(machine.state), "degraded") == 0);
}

static bool verify_test_signature(
    const edge_update_manifest_t *manifest,
    void *context
)
{
    const bool expected = *(const bool *)context;
    return expected && manifest->signature[0] == UINT8_C(0xA5);
}

static void test_update_manifest(void)
{
    edge_update_manifest_t manifest = {0};
    bool signature_is_valid = true;

    (void)strcpy(manifest.target, "edge18-rev-a");
    (void)strcpy(manifest.version, "1.2.3");
    manifest.security_counter = UINT32_C(8);
    manifest.image_size = UINT32_C(1024);
    manifest.image_sha256[0] = UINT8_C(0x5A);
    manifest.signature[0] = UINT8_C(0xA5);
    manifest.signature_length = 1U;
    assert(
        edge_update_manifest_validate(
            &manifest,
            "edge18-rev-a",
            UINT32_C(2048),
            UINT32_C(7),
            verify_test_signature,
            &signature_is_valid
        ) == EDGE_UPDATE_OK
    );
    manifest.security_counter = UINT32_C(7);
    assert(
        edge_update_manifest_validate(
            &manifest,
            "edge18-rev-a",
            UINT32_C(2048),
            UINT32_C(7),
            verify_test_signature,
            &signature_is_valid
        ) == EDGE_UPDATE_ROLLBACK_REJECTED
    );
}

static void test_telemetry_encoding(void)
{
    edge_point_record_t point = make_point(UINT64_C(19));
    char output[1024];
    size_t written = 0U;

    point.timestamp_ms = INT64_C(1785100000123);
    point.monotonic_ms = UINT64_C(623991);
    point.value_type = EDGE_VALUE_F64;
    point.value.f64 = 73.2;
    (void)strcpy(point.point_id, "tank.level");
    (void)strcpy(point.unit, "%");
    (void)strcpy(point.source, "ai1");
    assert(
        edge_telemetry_encode(
            "edge18-000001",
            "9f462527",
            UINT64_C(0x18A42),
            INT64_C(1785100000123),
            &point,
            1U,
            output,
            sizeof(output),
            &written
        ) == EDGE_TELEMETRY_OK
    );
    assert(written == strlen(output));
    assert(strstr(output, "\"schema\":\"edge.telemetry/1\"") != NULL);
    assert(strstr(output, "\"point_id\":\"tank.level\"") != NULL);
    assert(strstr(output, "\"quality\":0") != NULL);
    assert(strstr(output, "\"message_id\":\"0000000000018a42\"") != NULL);
}

int main(void)
{
    test_identifier_validation();
    test_quality();
    test_queue_reject_new();
    test_queue_drop_oldest_and_wrap();
    test_queue_invalid_arguments();
    test_modbus_crc();
    test_modbus_frames_and_decoding();
    test_configuration_validation();
    test_scheduler_backoff();
    test_journal_recovery();
    test_state_machine();
    test_update_manifest();
    test_telemetry_encoding();
    puts("edge_core_tests: PASS");
    return 0;
}
