#ifndef EDGE_JOURNAL_H
#define EDGE_JOURNAL_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EDGE_JOURNAL_HEADER_SIZE 24U
#define EDGE_JOURNAL_TRAILER_SIZE 4U
#define EDGE_JOURNAL_MAX_PAYLOAD 4096U

typedef enum {
    EDGE_JOURNAL_OK = 0,
    EDGE_JOURNAL_INVALID_ARGUMENT,
    EDGE_JOURNAL_BUFFER_TOO_SMALL,
    EDGE_JOURNAL_PAYLOAD_TOO_LARGE,
    EDGE_JOURNAL_CORRUPT,
    EDGE_JOURNAL_TORN_WRITE
} edge_journal_result_t;

typedef struct {
    uint64_t sequence;
    const uint8_t *payload;
    uint32_t payload_length;
    size_t record_length;
} edge_journal_record_t;

typedef struct {
    size_t valid_bytes;
    size_t record_count;
    uint64_t last_sequence;
    edge_journal_result_t stop_reason;
} edge_journal_scan_t;

uint32_t edge_crc32(const uint8_t *data, size_t length);

edge_journal_result_t edge_journal_encode(
    uint64_t sequence,
    const uint8_t *payload,
    uint32_t payload_length,
    uint8_t *output,
    size_t capacity,
    size_t *written
);

edge_journal_result_t edge_journal_decode(
    const uint8_t *input,
    size_t length,
    edge_journal_record_t *record
);

edge_journal_scan_t edge_journal_scan(
    const uint8_t *input,
    size_t length
);

#ifdef __cplusplus
}
#endif

#endif
