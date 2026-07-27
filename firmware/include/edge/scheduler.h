#ifndef EDGE_SCHEDULER_H
#define EDGE_SCHEDULER_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t period_ms;
    uint32_t max_backoff_ms;
    uint64_t next_due_ms;
    uint8_t consecutive_failures;
} edge_schedule_t;

bool edge_schedule_init(
    edge_schedule_t *schedule,
    uint32_t period_ms,
    uint32_t max_backoff_ms,
    uint64_t now_ms,
    uint32_t phase_ms
);

bool edge_schedule_is_due(
    const edge_schedule_t *schedule,
    uint64_t now_ms
);

void edge_schedule_complete(
    edge_schedule_t *schedule,
    uint64_t now_ms,
    bool success
);

#ifdef __cplusplus
}
#endif

#endif
