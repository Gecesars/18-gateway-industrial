#ifndef EDGE_MODBUS_H
#define EDGE_MODBUS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EDGE_MODBUS_REQUEST_SIZE 8U
#define EDGE_MODBUS_MAX_PDU_DATA 250U

typedef enum {
    EDGE_MODBUS_OK = 0,
    EDGE_MODBUS_INVALID_ARGUMENT,
    EDGE_MODBUS_BUFFER_TOO_SMALL,
    EDGE_MODBUS_INVALID_SLAVE,
    EDGE_MODBUS_INVALID_FUNCTION,
    EDGE_MODBUS_INVALID_QUANTITY,
    EDGE_MODBUS_TRUNCATED,
    EDGE_MODBUS_WRONG_SLAVE,
    EDGE_MODBUS_WRONG_FUNCTION,
    EDGE_MODBUS_CRC_ERROR,
    EDGE_MODBUS_EXCEPTION,
    EDGE_MODBUS_LENGTH_ERROR
} edge_modbus_result_t;

typedef enum {
    EDGE_MODBUS_ORDER_ABCD = 0,
    EDGE_MODBUS_ORDER_BADC,
    EDGE_MODBUS_ORDER_CDAB,
    EDGE_MODBUS_ORDER_DCBA
} edge_modbus_word_order_t;

typedef struct {
    const uint8_t *data;
    size_t data_length;
    uint8_t exception_code;
} edge_modbus_response_t;

edge_modbus_result_t edge_modbus_build_read_request(
    uint8_t slave,
    uint8_t function,
    uint16_t address,
    uint16_t quantity,
    uint8_t *frame,
    size_t capacity,
    size_t *frame_length
);

edge_modbus_result_t edge_modbus_parse_read_response(
    const uint8_t *frame,
    size_t frame_length,
    uint8_t expected_slave,
    uint8_t expected_function,
    edge_modbus_response_t *response
);

edge_modbus_result_t edge_modbus_decode_u16(
    const uint8_t *data,
    size_t length,
    int swap_bytes,
    uint16_t *value
);

edge_modbus_result_t edge_modbus_decode_u32(
    const uint8_t *data,
    size_t length,
    edge_modbus_word_order_t order,
    uint32_t *value
);

edge_modbus_result_t edge_modbus_decode_f32(
    const uint8_t *data,
    size_t length,
    edge_modbus_word_order_t order,
    float *value
);

#ifdef __cplusplus
}
#endif

#endif
