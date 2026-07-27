#include "edge/journal.h"

#include <string.h>

#define EDGE_JOURNAL_MAGIC UINT32_C(0x38314445)
#define EDGE_JOURNAL_VERSION UINT16_C(1)
#define EDGE_JOURNAL_COMMIT UINT32_C(0xC04D17ED)

static void edge_store_u16(uint8_t *output, uint16_t value)
{
    output[0] = (uint8_t)(value & UINT16_C(0x00FF));
    output[1] = (uint8_t)(value >> 8U);
}

static void edge_store_u32(uint8_t *output, uint32_t value)
{
    output[0] = (uint8_t)(value & UINT32_C(0x000000FF));
    output[1] = (uint8_t)((value >> 8U) & UINT32_C(0x000000FF));
    output[2] = (uint8_t)((value >> 16U) & UINT32_C(0x000000FF));
    output[3] = (uint8_t)(value >> 24U);
}

static void edge_store_u64(uint8_t *output, uint64_t value)
{
    unsigned int index = 0U;

    for (index = 0U; index < 8U; ++index) {
        output[index] = (uint8_t)(value >> (index * 8U));
    }
}

static uint16_t edge_load_u16(const uint8_t *input)
{
    return (uint16_t)input[0] | (uint16_t)((uint16_t)input[1] << 8U);
}

static uint32_t edge_load_u32(const uint8_t *input)
{
    return (uint32_t)input[0]
        | ((uint32_t)input[1] << 8U)
        | ((uint32_t)input[2] << 16U)
        | ((uint32_t)input[3] << 24U);
}

static uint64_t edge_load_u64(const uint8_t *input)
{
    uint64_t value = 0U;
    unsigned int index = 0U;

    for (index = 0U; index < 8U; ++index) {
        value |= (uint64_t)input[index] << (index * 8U);
    }
    return value;
}

uint32_t edge_crc32(const uint8_t *data, size_t length)
{
    uint32_t crc = UINT32_C(0xFFFFFFFF);
    size_t index = 0U;

    if (data == NULL && length > 0U) {
        return 0U;
    }
    for (index = 0U; index < length; ++index) {
        unsigned int bit = 0U;
        crc ^= data[index];
        for (bit = 0U; bit < 8U; ++bit) {
            const uint32_t mask = (uint32_t)(0U - (crc & 1U));
            crc = (crc >> 1U) ^ (UINT32_C(0xEDB88320) & mask);
        }
    }
    return ~crc;
}

edge_journal_result_t edge_journal_encode(
    uint64_t sequence,
    const uint8_t *payload,
    uint32_t payload_length,
    uint8_t *output,
    size_t capacity,
    size_t *written
)
{
    size_t required = 0U;

    if (output == NULL || written == NULL) {
        return EDGE_JOURNAL_INVALID_ARGUMENT;
    }
    *written = 0U;
    if (payload == NULL && payload_length > 0U) {
        return EDGE_JOURNAL_INVALID_ARGUMENT;
    }
    if (payload_length > EDGE_JOURNAL_MAX_PAYLOAD) {
        return EDGE_JOURNAL_PAYLOAD_TOO_LARGE;
    }
    required =
        EDGE_JOURNAL_HEADER_SIZE
        + (size_t)payload_length
        + EDGE_JOURNAL_TRAILER_SIZE;
    if (capacity < required) {
        return EDGE_JOURNAL_BUFFER_TOO_SMALL;
    }

    edge_store_u32(&output[0], EDGE_JOURNAL_MAGIC);
    edge_store_u16(&output[4], EDGE_JOURNAL_VERSION);
    edge_store_u16(&output[6], (uint16_t)EDGE_JOURNAL_HEADER_SIZE);
    edge_store_u64(&output[8], sequence);
    edge_store_u32(&output[16], payload_length);
    edge_store_u32(&output[20], edge_crc32(payload, payload_length));
    if (payload_length > 0U) {
        (void)memcpy(
            &output[EDGE_JOURNAL_HEADER_SIZE],
            payload,
            payload_length
        );
    }
    edge_store_u32(
        &output[EDGE_JOURNAL_HEADER_SIZE + (size_t)payload_length],
        EDGE_JOURNAL_COMMIT
    );
    *written = required;
    return EDGE_JOURNAL_OK;
}

edge_journal_result_t edge_journal_decode(
    const uint8_t *input,
    size_t length,
    edge_journal_record_t *record
)
{
    uint32_t payload_length = 0U;
    size_t required = 0U;
    const uint8_t *payload = NULL;

    if (input == NULL || record == NULL) {
        return EDGE_JOURNAL_INVALID_ARGUMENT;
    }
    if (length < EDGE_JOURNAL_HEADER_SIZE) {
        return EDGE_JOURNAL_TORN_WRITE;
    }
    if (
        edge_load_u32(&input[0]) != EDGE_JOURNAL_MAGIC
        || edge_load_u16(&input[4]) != EDGE_JOURNAL_VERSION
        || edge_load_u16(&input[6]) != EDGE_JOURNAL_HEADER_SIZE
    ) {
        return EDGE_JOURNAL_CORRUPT;
    }
    payload_length = edge_load_u32(&input[16]);
    if (payload_length > EDGE_JOURNAL_MAX_PAYLOAD) {
        return EDGE_JOURNAL_CORRUPT;
    }
    required =
        EDGE_JOURNAL_HEADER_SIZE
        + (size_t)payload_length
        + EDGE_JOURNAL_TRAILER_SIZE;
    if (length < required) {
        return EDGE_JOURNAL_TORN_WRITE;
    }
    payload = &input[EDGE_JOURNAL_HEADER_SIZE];
    if (
        edge_load_u32(&input[required - EDGE_JOURNAL_TRAILER_SIZE])
        != EDGE_JOURNAL_COMMIT
    ) {
        return EDGE_JOURNAL_TORN_WRITE;
    }
    if (edge_crc32(payload, payload_length) != edge_load_u32(&input[20])) {
        return EDGE_JOURNAL_CORRUPT;
    }
    record->sequence = edge_load_u64(&input[8]);
    record->payload = payload;
    record->payload_length = payload_length;
    record->record_length = required;
    return EDGE_JOURNAL_OK;
}

edge_journal_scan_t edge_journal_scan(
    const uint8_t *input,
    size_t length
)
{
    edge_journal_scan_t scan = {0U, 0U, 0U, EDGE_JOURNAL_OK};

    if (input == NULL && length > 0U) {
        scan.stop_reason = EDGE_JOURNAL_INVALID_ARGUMENT;
        return scan;
    }
    while (scan.valid_bytes < length) {
        edge_journal_record_t record = {0U, NULL, 0U, 0U};
        const edge_journal_result_t result = edge_journal_decode(
            &input[scan.valid_bytes],
            length - scan.valid_bytes,
            &record
        );

        if (result != EDGE_JOURNAL_OK) {
            scan.stop_reason = result;
            return scan;
        }
        scan.valid_bytes += record.record_length;
        ++scan.record_count;
        scan.last_sequence = record.sequence;
    }
    return scan;
}
