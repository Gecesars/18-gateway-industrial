#include "edge/telemetry.h"

#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

static bool edge_append_format(
    char *output,
    size_t capacity,
    size_t *offset,
    const char *format,
    ...
)
{
    va_list arguments;
    int count = 0;

    if (*offset >= capacity) {
        return false;
    }
    va_start(arguments, format);
    count = vsnprintf(
        &output[*offset],
        capacity - *offset,
        format,
        arguments
    );
    va_end(arguments);
    if (count < 0 || (size_t)count >= capacity - *offset) {
        return false;
    }
    *offset += (size_t)count;
    return true;
}

static bool edge_append_json_string(
    char *output,
    size_t capacity,
    size_t *offset,
    const char *value,
    size_t value_capacity
)
{
    size_t index = 0U;

    if (value == NULL || !edge_append_format(output, capacity, offset, "\"")) {
        return false;
    }
    while (index < value_capacity && value[index] != '\0') {
        const unsigned char character = (unsigned char)value[index];
        const char *escape = NULL;

        if (character == (unsigned char)'\"') {
            escape = "\\\"";
        } else if (character == (unsigned char)'\\') {
            escape = "\\\\";
        } else if (character == (unsigned char)'\b') {
            escape = "\\b";
        } else if (character == (unsigned char)'\f') {
            escape = "\\f";
        } else if (character == (unsigned char)'\n') {
            escape = "\\n";
        } else if (character == (unsigned char)'\r') {
            escape = "\\r";
        } else if (character == (unsigned char)'\t') {
            escape = "\\t";
        }
        if (escape != NULL) {
            if (!edge_append_format(output, capacity, offset, "%s", escape)) {
                return false;
            }
        } else if (character < UINT8_C(0x20)) {
            if (!edge_append_format(
                    output,
                    capacity,
                    offset,
                    "\\u%04x",
                    (unsigned int)character
                )) {
                return false;
            }
        } else if (!edge_append_format(
                output,
                capacity,
                offset,
                "%c",
                (int)character
            )) {
            return false;
        }
        ++index;
    }
    if (index == value_capacity) {
        return false;
    }
    return edge_append_format(output, capacity, offset, "\"");
}

static bool edge_boot_id_is_valid(const char *boot_id)
{
    size_t length = 0U;

    if (boot_id == NULL) {
        return false;
    }
    while (length <= 32U && boot_id[length] != '\0') {
        const char character = boot_id[length];
        if (
            !((character >= '0' && character <= '9')
                || (character >= 'a' && character <= 'f'))
        ) {
            return false;
        }
        ++length;
    }
    return length >= 8U && length <= 32U;
}

static const char *edge_value_type_name(edge_value_type_t type)
{
    static const char *const names[] = {
        "bool",
        "i64",
        "u64",
        "f64",
        "string"
    };

    if ((unsigned int)type >= sizeof(names) / sizeof(names[0])) {
        return NULL;
    }
    return names[type];
}

static bool edge_append_value(
    char *output,
    size_t capacity,
    size_t *offset,
    const edge_point_record_t *point
)
{
    switch (point->value_type) {
    case EDGE_VALUE_BOOL:
        return edge_append_format(
            output,
            capacity,
            offset,
            "%s",
            point->value.boolean ? "true" : "false"
        );
    case EDGE_VALUE_I64:
        return edge_append_format(
            output,
            capacity,
            offset,
            "%lld",
            (long long)point->value.i64
        );
    case EDGE_VALUE_U64:
        return edge_append_format(
            output,
            capacity,
            offset,
            "%llu",
            (unsigned long long)point->value.u64
        );
    case EDGE_VALUE_F64:
        return isfinite(point->value.f64)
            && edge_append_format(
                output,
                capacity,
                offset,
                "%.17g",
                point->value.f64
            );
    case EDGE_VALUE_STRING:
        return edge_append_json_string(
            output,
            capacity,
            offset,
            point->value.string,
            sizeof(point->value.string)
        );
    default:
        return false;
    }
}

static bool edge_append_point(
    char *output,
    size_t capacity,
    size_t *offset,
    const edge_point_record_t *point
)
{
    const char *type_name = edge_value_type_name(point->value_type);

    if (
        type_name == NULL
        || point->timestamp_ms < 0
        || !edge_point_identifier_is_valid(
            point->point_id,
            sizeof(point->point_id)
        )
    ) {
        return false;
    }
    if (!edge_append_format(output, capacity, offset, "{\"point_id\":")) {
        return false;
    }
    if (!edge_append_json_string(
            output,
            capacity,
            offset,
            point->point_id,
            sizeof(point->point_id)
        )
        || !edge_append_format(
            output,
            capacity,
            offset,
            ",\"sequence\":%llu,\"timestamp_ms\":%lld,"
            "\"monotonic_ms\":%llu,\"value_type\":\"%s\",\"value\":",
            (unsigned long long)point->sequence,
            (long long)point->timestamp_ms,
            (unsigned long long)point->monotonic_ms,
            type_name
        )
        || !edge_append_value(output, capacity, offset, point)
        || !edge_append_format(output, capacity, offset, ",\"unit\":")
        || !edge_append_json_string(
            output,
            capacity,
            offset,
            point->unit,
            sizeof(point->unit)
        )
        || !edge_append_format(
            output,
            capacity,
            offset,
            ",\"quality\":%lu,\"source\":",
            (unsigned long)point->quality
        )
        || !edge_append_json_string(
            output,
            capacity,
            offset,
            point->source,
            sizeof(point->source)
        )
        || !edge_append_format(
            output,
            capacity,
            offset,
            ",\"config_revision\":%lu}",
            (unsigned long)point->config_revision
        )) {
        return false;
    }
    return point->config_revision > 0U;
}

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
)
{
    size_t offset = 0U;
    size_t index = 0U;

    if (
        device_id == NULL
        || boot_id == NULL
        || points == NULL
        || output == NULL
        || written == NULL
        || capacity == 0U
    ) {
        return EDGE_TELEMETRY_INVALID_ARGUMENT;
    }
    *written = 0U;
    output[0] = '\0';
    if (
        !edge_point_identifier_is_valid(
            device_id,
            EDGE_POINT_ID_CAPACITY
        )
        || !edge_boot_id_is_valid(boot_id)
        || sent_at_ms < 0
        || point_count == 0U
        || point_count > 128U
    ) {
        return EDGE_TELEMETRY_INVALID_ARGUMENT;
    }
    if (!edge_append_format(
            output,
            capacity,
            &offset,
            "{\"schema\":\"edge.telemetry/1\",\"device_id\":"
        )
        || !edge_append_json_string(
            output,
            capacity,
            &offset,
            device_id,
            EDGE_POINT_ID_CAPACITY
        )
        || !edge_append_format(output, capacity, &offset, ",\"boot_id\":")
        || !edge_append_json_string(
            output,
            capacity,
            &offset,
            boot_id,
            33U
        )
        || !edge_append_format(
            output,
            capacity,
            &offset,
            ",\"message_id\":\"%016llx\",\"sent_at_ms\":%lld,\"points\":[",
            (unsigned long long)message_id,
            (long long)sent_at_ms
        )) {
        return EDGE_TELEMETRY_BUFFER_TOO_SMALL;
    }
    for (index = 0U; index < point_count; ++index) {
        if (
            (index > 0U
                && !edge_append_format(output, capacity, &offset, ","))
            || !edge_append_point(output, capacity, &offset, &points[index])
        ) {
            return edge_value_type_name(points[index].value_type) == NULL
                || points[index].config_revision == 0U
                ? EDGE_TELEMETRY_INVALID_POINT
                : EDGE_TELEMETRY_BUFFER_TOO_SMALL;
        }
    }
    if (!edge_append_format(output, capacity, &offset, "]}")) {
        return EDGE_TELEMETRY_BUFFER_TOO_SMALL;
    }
    *written = offset;
    return EDGE_TELEMETRY_OK;
}
