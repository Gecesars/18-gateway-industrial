#ifndef EDGE_CONFIG_H
#define EDGE_CONFIG_H

#include "edge/point.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EDGE_CONFIG_MAX_DEVICES 32U
#define EDGE_CONFIG_MAX_POINTS 128U

typedef enum {
    EDGE_CONFIG_PORT_RS485_A = 0,
    EDGE_CONFIG_PORT_RS485_B
} edge_config_port_t;

typedef enum {
    EDGE_CONFIG_PARITY_NONE = 0,
    EDGE_CONFIG_PARITY_EVEN,
    EDGE_CONFIG_PARITY_ODD
} edge_config_parity_t;

typedef enum {
    EDGE_CONFIG_SOURCE_MODBUS = 0,
    EDGE_CONFIG_SOURCE_ANALOG,
    EDGE_CONFIG_SOURCE_DIGITAL
} edge_config_source_t;

typedef struct {
    char id[EDGE_POINT_ID_CAPACITY];
    edge_config_port_t port;
    uint8_t slave;
    uint32_t baud;
    edge_config_parity_t parity;
    uint32_t timeout_ms;
    uint8_t retries;
} edge_modbus_device_config_t;

typedef struct {
    char id[EDGE_POINT_ID_CAPACITY];
    edge_config_source_t source;
    uint32_t period_ms;
    uint32_t stale_ms;
    uint8_t channel;
    uint8_t modbus_device_index;
    uint8_t modbus_function;
    uint16_t modbus_address;
    uint16_t modbus_quantity;
} edge_point_config_t;

typedef struct {
    uint32_t revision;
    const edge_modbus_device_config_t *devices;
    size_t device_count;
    const edge_point_config_t *points;
    size_t point_count;
} edge_runtime_config_t;

typedef enum {
    EDGE_CONFIG_OK = 0,
    EDGE_CONFIG_INVALID_ARGUMENT,
    EDGE_CONFIG_INVALID_REVISION,
    EDGE_CONFIG_TOO_MANY_DEVICES,
    EDGE_CONFIG_TOO_MANY_POINTS,
    EDGE_CONFIG_INVALID_IDENTIFIER,
    EDGE_CONFIG_DUPLICATE_IDENTIFIER,
    EDGE_CONFIG_INVALID_SERIAL,
    EDGE_CONFIG_INVALID_POINT,
    EDGE_CONFIG_INVALID_REFERENCE
} edge_config_result_t;

typedef struct {
    edge_config_result_t code;
    size_t index;
    const char *field;
} edge_config_error_t;

edge_config_result_t edge_config_validate(
    const edge_runtime_config_t *config,
    edge_config_error_t *error
);

#ifdef __cplusplus
}
#endif

#endif
