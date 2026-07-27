#include "edge/modbus_crc.h"
#include "edge/point.h"
#include "edge/queue.h"

#include <assert.h>
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

int main(void)
{
    test_identifier_validation();
    test_quality();
    test_queue_reject_new();
    test_queue_drop_oldest_and_wrap();
    test_queue_invalid_arguments();
    test_modbus_crc();
    puts("edge_core_tests: PASS");
    return 0;
}
