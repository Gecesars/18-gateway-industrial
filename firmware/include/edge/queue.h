#ifndef EDGE_QUEUE_H
#define EDGE_QUEUE_H

#include "edge/point.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    EDGE_QUEUE_REJECT_NEW = 0,
    EDGE_QUEUE_DROP_OLDEST
} edge_queue_overflow_policy_t;

typedef enum {
    EDGE_QUEUE_OK = 0,
    EDGE_QUEUE_INVALID_ARGUMENT,
    EDGE_QUEUE_EMPTY,
    EDGE_QUEUE_FULL
} edge_queue_result_t;

typedef struct {
    edge_point_record_t *records;
    size_t capacity;
    size_t head;
    size_t count;
    uint64_t pushed_total;
    uint64_t popped_total;
    uint64_t dropped_total;
    edge_queue_overflow_policy_t overflow_policy;
} edge_queue_t;

edge_queue_result_t edge_queue_init(
    edge_queue_t *queue,
    edge_point_record_t *storage,
    size_t capacity,
    edge_queue_overflow_policy_t policy
);

edge_queue_result_t edge_queue_push(
    edge_queue_t *queue,
    const edge_point_record_t *point
);

edge_queue_result_t edge_queue_peek(
    const edge_queue_t *queue,
    edge_point_record_t *point
);

edge_queue_result_t edge_queue_pop(
    edge_queue_t *queue,
    edge_point_record_t *point
);

size_t edge_queue_count(const edge_queue_t *queue);
bool edge_queue_is_empty(const edge_queue_t *queue);
bool edge_queue_is_full(const edge_queue_t *queue);

#ifdef __cplusplus
}
#endif

#endif
