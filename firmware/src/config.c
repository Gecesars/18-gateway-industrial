#include "edge/config.h"

#include <stdbool.h>
#include <string.h>

static bool edge_baud_is_supported(uint32_t baud)
{
    static const uint32_t supported[] = {
        UINT32_C(1200),
        UINT32_C(2400),
        UINT32_C(4800),
        UINT32_C(9600),
        UINT32_C(19200),
        UINT32_C(38400),
        UINT32_C(57600),
        UINT32_C(115200)
    };
    size_t index = 0U;

    for (index = 0U; index < sizeof(supported) / sizeof(supported[0]); ++index) {
        if (supported[index] == baud) {
            return true;
        }
    }
    return false;
}

static edge_config_result_t edge_config_fail(
    edge_config_error_t *error,
    edge_config_result_t code,
    size_t index,
    const char *field
)
{
    if (error != NULL) {
        error->code = code;
        error->index = index;
        error->field = field;
    }
    return code;
}

static bool edge_identifier_equals(
    const char *left,
    const char *right
)
{
    return strncmp(left, right, EDGE_POINT_ID_CAPACITY) == 0;
}

edge_config_result_t edge_config_validate(
    const edge_runtime_config_t *config,
    edge_config_error_t *error
)
{
    size_t index = 0U;

    if (error != NULL) {
        error->code = EDGE_CONFIG_OK;
        error->index = 0U;
        error->field = "";
    }
    if (config == NULL) {
        return edge_config_fail(
            error,
            EDGE_CONFIG_INVALID_ARGUMENT,
            0U,
            "config"
        );
    }
    if (config->revision == 0U) {
        return edge_config_fail(
            error,
            EDGE_CONFIG_INVALID_REVISION,
            0U,
            "revision"
        );
    }
    if (config->device_count > EDGE_CONFIG_MAX_DEVICES) {
        return edge_config_fail(
            error,
            EDGE_CONFIG_TOO_MANY_DEVICES,
            config->device_count,
            "devices"
        );
    }
    if (config->point_count > EDGE_CONFIG_MAX_POINTS) {
        return edge_config_fail(
            error,
            EDGE_CONFIG_TOO_MANY_POINTS,
            config->point_count,
            "points"
        );
    }
    if (
        (config->device_count > 0U && config->devices == NULL)
        || (config->point_count > 0U && config->points == NULL)
    ) {
        return edge_config_fail(
            error,
            EDGE_CONFIG_INVALID_ARGUMENT,
            0U,
            "table"
        );
    }

    for (index = 0U; index < config->device_count; ++index) {
        const edge_modbus_device_config_t *device = &config->devices[index];
        size_t previous = 0U;

        if (!edge_point_identifier_is_valid(
                device->id,
                sizeof(device->id)
            )) {
            return edge_config_fail(
                error,
                EDGE_CONFIG_INVALID_IDENTIFIER,
                index,
                "devices.id"
            );
        }
        for (previous = 0U; previous < index; ++previous) {
            if (edge_identifier_equals(
                    device->id,
                    config->devices[previous].id
                )) {
                return edge_config_fail(
                    error,
                    EDGE_CONFIG_DUPLICATE_IDENTIFIER,
                    index,
                    "devices.id"
                );
            }
        }
        if (
            device->port > EDGE_CONFIG_PORT_RS485_B
            || device->slave == 0U
            || device->slave > 247U
            || !edge_baud_is_supported(device->baud)
            || device->parity > EDGE_CONFIG_PARITY_ODD
            || device->timeout_ms < 20U
            || device->timeout_ms > 10000U
            || device->retries > 5U
        ) {
            return edge_config_fail(
                error,
                EDGE_CONFIG_INVALID_SERIAL,
                index,
                "devices.serial"
            );
        }
    }

    for (index = 0U; index < config->point_count; ++index) {
        const edge_point_config_t *point = &config->points[index];
        size_t previous = 0U;

        if (!edge_point_identifier_is_valid(
                point->id,
                sizeof(point->id)
            )) {
            return edge_config_fail(
                error,
                EDGE_CONFIG_INVALID_IDENTIFIER,
                index,
                "points.id"
            );
        }
        for (previous = 0U; previous < index; ++previous) {
            if (edge_identifier_equals(
                    point->id,
                    config->points[previous].id
                )) {
                return edge_config_fail(
                    error,
                    EDGE_CONFIG_DUPLICATE_IDENTIFIER,
                    index,
                    "points.id"
                );
            }
        }
        if (
            point->source > EDGE_CONFIG_SOURCE_DIGITAL
            || point->period_ms < 10U
            || point->stale_ms < point->period_ms
        ) {
            return edge_config_fail(
                error,
                EDGE_CONFIG_INVALID_POINT,
                index,
                "points.timing"
            );
        }
        if (point->source == EDGE_CONFIG_SOURCE_MODBUS) {
            const bool coils =
                point->modbus_function == 1U
                || point->modbus_function == 2U;
            const bool registers =
                point->modbus_function == 3U
                || point->modbus_function == 4U;
            const bool quantity_valid =
                (coils
                    && point->modbus_quantity >= 1U
                    && point->modbus_quantity <= 2000U)
                || (registers
                    && point->modbus_quantity >= 1U
                    && point->modbus_quantity <= 125U);

            if (
                point->modbus_device_index >= config->device_count
                || !quantity_valid
            ) {
                return edge_config_fail(
                    error,
                    EDGE_CONFIG_INVALID_REFERENCE,
                    index,
                    "points.modbus"
                );
            }
        } else if (point->channel < 1U || point->channel > 4U) {
            return edge_config_fail(
                error,
                EDGE_CONFIG_INVALID_POINT,
                index,
                "points.channel"
            );
        }
    }

    return EDGE_CONFIG_OK;
}
