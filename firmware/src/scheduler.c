#include "edge/scheduler.h"

#include <limits.h>
#include <stddef.h>

static uint64_t edge_add_saturating(uint64_t left, uint64_t right)
{
    if (UINT64_MAX - left < right) {
        return UINT64_MAX;
    }
    return left + right;
}

bool edge_schedule_init(
    edge_schedule_t *schedule,
    uint32_t period_ms,
    uint32_t max_backoff_ms,
    uint64_t now_ms,
    uint32_t phase_ms
)
{
    if (
        schedule == NULL
        || period_ms == 0U
        || max_backoff_ms < period_ms
        || phase_ms >= period_ms
    ) {
        return false;
    }
    schedule->period_ms = period_ms;
    schedule->max_backoff_ms = max_backoff_ms;
    schedule->next_due_ms = edge_add_saturating(now_ms, phase_ms);
    schedule->consecutive_failures = 0U;
    return true;
}

bool edge_schedule_is_due(
    const edge_schedule_t *schedule,
    uint64_t now_ms
)
{
    return schedule != NULL
        && schedule->period_ms > 0U
        && now_ms >= schedule->next_due_ms;
}

void edge_schedule_complete(
    edge_schedule_t *schedule,
    uint64_t now_ms,
    bool success
)
{
    uint64_t delay = 0U;
    unsigned int shift = 0U;

    if (schedule == NULL || schedule->period_ms == 0U) {
        return;
    }
    if (success) {
        schedule->consecutive_failures = 0U;
        delay = schedule->period_ms;
    } else {
        if (schedule->consecutive_failures < UINT8_MAX) {
            ++schedule->consecutive_failures;
        }
        shift = schedule->consecutive_failures > 15U
            ? 15U
            : schedule->consecutive_failures;
        delay = (uint64_t)schedule->period_ms << shift;
        if (delay > schedule->max_backoff_ms) {
            delay = schedule->max_backoff_ms;
        }
    }
    schedule->next_due_ms = edge_add_saturating(now_ms, delay);
}
