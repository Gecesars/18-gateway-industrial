#ifndef EDGE_POINT_H
#define EDGE_POINT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EDGE_POINT_ID_CAPACITY 49U
#define EDGE_UNIT_CAPACITY 17U
#define EDGE_SOURCE_CAPACITY 33U
#define EDGE_STRING_CAPACITY 65U

typedef uint32_t edge_quality_t;

enum edge_quality_flag {
    EDGE_QUALITY_GOOD = 0U,
    EDGE_QUALITY_COMM_TIMEOUT = 1U << 0,
    EDGE_QUALITY_COMM_CRC = 1U << 1,
    EDGE_QUALITY_PROTOCOL_EXCEPTION = 1U << 2,
    EDGE_QUALITY_OUT_OF_RANGE = 1U << 3,
    EDGE_QUALITY_SENSOR_FAULT = 1U << 4,
    EDGE_QUALITY_STALE = 1U << 5,
    EDGE_QUALITY_TIME_UNSYNCED = 1U << 6,
    EDGE_QUALITY_CONVERSION_ERROR = 1U << 7,
    EDGE_QUALITY_CONFIG_ERROR = 1U << 8,
    EDGE_QUALITY_STORAGE_DEGRADED = 1U << 9
};

typedef enum {
    EDGE_VALUE_BOOL = 0,
    EDGE_VALUE_I64,
    EDGE_VALUE_U64,
    EDGE_VALUE_F64,
    EDGE_VALUE_STRING
} edge_value_type_t;

typedef union {
    bool boolean;
    int64_t i64;
    uint64_t u64;
    double f64;
    char string[EDGE_STRING_CAPACITY];
} edge_value_t;

typedef struct {
    char point_id[EDGE_POINT_ID_CAPACITY];
    uint64_t sequence;
    int64_t timestamp_ms;
    uint64_t monotonic_ms;
    edge_value_type_t value_type;
    edge_value_t value;
    char unit[EDGE_UNIT_CAPACITY];
    edge_quality_t quality;
    char source[EDGE_SOURCE_CAPACITY];
    uint32_t config_revision;
} edge_point_record_t;

bool edge_point_is_good(const edge_point_record_t *point);
bool edge_point_has_quality(
    const edge_point_record_t *point,
    edge_quality_t flag
);
void edge_point_add_quality(edge_point_record_t *point, edge_quality_t flag);
void edge_point_clear_quality(edge_point_record_t *point, edge_quality_t flag);
bool edge_point_identifier_is_valid(const char *identifier, size_t capacity);

#ifdef __cplusplus
}
#endif

#endif
