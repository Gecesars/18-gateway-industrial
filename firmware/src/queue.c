#include "edge/queue.h"

static bool edge_queue_is_valid(const edge_queue_t *queue)
{
    return queue != NULL &&
        queue->records != NULL &&
        queue->capacity > 0U &&
        queue->head < queue->capacity &&
        queue->count <= queue->capacity;
}

edge_queue_result_t edge_queue_init(
    edge_queue_t *queue,
    edge_point_record_t *storage,
    size_t capacity,
    edge_queue_overflow_policy_t policy
)
{
    if (queue == NULL || storage == NULL || capacity == 0U) {
        return EDGE_QUEUE_INVALID_ARGUMENT;
    }

    if (policy != EDGE_QUEUE_REJECT_NEW &&
        policy != EDGE_QUEUE_DROP_OLDEST) {
        return EDGE_QUEUE_INVALID_ARGUMENT;
    }

    queue->records = storage;
    queue->capacity = capacity;
    queue->head = 0U;
    queue->count = 0U;
    queue->pushed_total = 0U;
    queue->popped_total = 0U;
    queue->dropped_total = 0U;
    queue->overflow_policy = policy;
    return EDGE_QUEUE_OK;
}

edge_queue_result_t edge_queue_push(
    edge_queue_t *queue,
    const edge_point_record_t *point
)
{
    size_t tail = 0U;

    if (!edge_queue_is_valid(queue) || point == NULL) {
        return EDGE_QUEUE_INVALID_ARGUMENT;
    }

    if (queue->count == queue->capacity) {
        if (queue->overflow_policy == EDGE_QUEUE_REJECT_NEW) {
            return EDGE_QUEUE_FULL;
        }

        queue->head = (queue->head + 1U) % queue->capacity;
        --queue->count;
        ++queue->dropped_total;
    }

    tail = (queue->head + queue->count) % queue->capacity;
    queue->records[tail] = *point;
    ++queue->count;
    ++queue->pushed_total;
    return EDGE_QUEUE_OK;
}

edge_queue_result_t edge_queue_peek(
    const edge_queue_t *queue,
    edge_point_record_t *point
)
{
    if (!edge_queue_is_valid(queue) || point == NULL) {
        return EDGE_QUEUE_INVALID_ARGUMENT;
    }

    if (queue->count == 0U) {
        return EDGE_QUEUE_EMPTY;
    }

    *point = queue->records[queue->head];
    return EDGE_QUEUE_OK;
}

edge_queue_result_t edge_queue_pop(
    edge_queue_t *queue,
    edge_point_record_t *point
)
{
    edge_queue_result_t result = EDGE_QUEUE_OK;

    if (!edge_queue_is_valid(queue) || point == NULL) {
        return EDGE_QUEUE_INVALID_ARGUMENT;
    }

    result = edge_queue_peek(queue, point);
    if (result != EDGE_QUEUE_OK) {
        return result;
    }

    queue->head = (queue->head + 1U) % queue->capacity;
    --queue->count;
    ++queue->popped_total;
    return EDGE_QUEUE_OK;
}

size_t edge_queue_count(const edge_queue_t *queue)
{
    return edge_queue_is_valid(queue) ? queue->count : 0U;
}

bool edge_queue_is_empty(const edge_queue_t *queue)
{
    return edge_queue_is_valid(queue) && queue->count == 0U;
}

bool edge_queue_is_full(const edge_queue_t *queue)
{
    return edge_queue_is_valid(queue) &&
        queue->count == queue->capacity;
}
