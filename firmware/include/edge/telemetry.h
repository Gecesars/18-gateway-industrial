#ifndef EDGE_TELEMETRY_H
#define EDGE_TELEMETRY_H

#include "edge/point.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    EDGE_TELEMETRY_OK = 0,
    EDGE_TELEMETRY_INVALID_ARGUMENT,
    EDGE_TELEMETRY_BUFFER_TOO_SMALL,
    EDGE_TELEMETRY_INVALID_POINT
} edge_telemetry_result_t;

edge_telemetry_result_t edge_telemetry_encode(
    const char *device_id,
    const char *boot_id,
    uint64_t message_id,
    int64_t sent_at_ms,
    const edge_point_record_t *points,
    size_t point_count,
    char *output,
    size_t capacity,
    size_t *written
);

#ifdef __cplusplus
}
#endif

#endif
