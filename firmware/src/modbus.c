#include "edge/modbus.h"

#include "edge/modbus_crc.h"

#include <string.h>

static void edge_write_u16_be(uint8_t *output, uint16_t value)
{
    output[0] = (uint8_t)(value >> 8U);
    output[1] = (uint8_t)(value & UINT16_C(0x00FF));
}

edge_modbus_result_t edge_modbus_build_read_request(
    uint8_t slave,
    uint8_t function,
    uint16_t address,
    uint16_t quantity,
    uint8_t *frame,
    size_t capacity,
    size_t *frame_length
)
{
    uint16_t crc = 0U;
    uint16_t maximum = 0U;

    if (frame == NULL || frame_length == NULL) {
        return EDGE_MODBUS_INVALID_ARGUMENT;
    }
    *frame_length = 0U;
    if (capacity < EDGE_MODBUS_REQUEST_SIZE) {
        return EDGE_MODBUS_BUFFER_TOO_SMALL;
    }
    if (slave == 0U || slave > 247U) {
        return EDGE_MODBUS_INVALID_SLAVE;
    }
    if (function < 1U || function > 4U) {
        return EDGE_MODBUS_INVALID_FUNCTION;
    }
    maximum = function <= 2U ? UINT16_C(2000) : UINT16_C(125);
    if (quantity == 0U || quantity > maximum) {
        return EDGE_MODBUS_INVALID_QUANTITY;
    }

    frame[0] = slave;
    frame[1] = function;
    edge_write_u16_be(&frame[2], address);
    edge_write_u16_be(&frame[4], quantity);
    crc = edge_modbus_crc16(frame, 6U);
    frame[6] = (uint8_t)(crc & UINT16_C(0x00FF));
    frame[7] = (uint8_t)(crc >> 8U);
    *frame_length = EDGE_MODBUS_REQUEST_SIZE;
    return EDGE_MODBUS_OK;
}

edge_modbus_result_t edge_modbus_parse_read_response(
    const uint8_t *frame,
    size_t frame_length,
    uint8_t expected_slave,
    uint8_t expected_function,
    edge_modbus_response_t *response
)
{
    uint16_t received_crc = 0U;
    uint16_t calculated_crc = 0U;
    size_t byte_count = 0U;

    if (frame == NULL || response == NULL) {
        return EDGE_MODBUS_INVALID_ARGUMENT;
    }
    response->data = NULL;
    response->data_length = 0U;
    response->exception_code = 0U;
    if (frame_length < 5U) {
        return EDGE_MODBUS_TRUNCATED;
    }
    received_crc =
        (uint16_t)frame[frame_length - 2U]
        | (uint16_t)((uint16_t)frame[frame_length - 1U] << 8U);
    calculated_crc = edge_modbus_crc16(frame, frame_length - 2U);
    if (received_crc != calculated_crc) {
        return EDGE_MODBUS_CRC_ERROR;
    }
    if (frame[0] != expected_slave) {
        return EDGE_MODBUS_WRONG_SLAVE;
    }
    if (frame[1] == (uint8_t)(expected_function | UINT8_C(0x80))) {
        if (frame_length != 5U) {
            return EDGE_MODBUS_LENGTH_ERROR;
        }
        response->exception_code = frame[2];
        return EDGE_MODBUS_EXCEPTION;
    }
    if (frame[1] != expected_function) {
        return EDGE_MODBUS_WRONG_FUNCTION;
    }
    byte_count = (size_t)frame[2];
    if (
        byte_count > EDGE_MODBUS_MAX_PDU_DATA
        || frame_length != byte_count + 5U
    ) {
        return EDGE_MODBUS_LENGTH_ERROR;
    }
    response->data = &frame[3];
    response->data_length = byte_count;
    return EDGE_MODBUS_OK;
}

edge_modbus_result_t edge_modbus_decode_u16(
    const uint8_t *data,
    size_t length,
    int swap_bytes,
    uint16_t *value
)
{
    if (data == NULL || value == NULL) {
        return EDGE_MODBUS_INVALID_ARGUMENT;
    }
    if (length < 2U) {
        return EDGE_MODBUS_TRUNCATED;
    }
    if (swap_bytes != 0) {
        *value = (uint16_t)((uint16_t)data[1] << 8U) | data[0];
    } else {
        *value = (uint16_t)((uint16_t)data[0] << 8U) | data[1];
    }
    return EDGE_MODBUS_OK;
}

edge_modbus_result_t edge_modbus_decode_u32(
    const uint8_t *data,
    size_t length,
    edge_modbus_word_order_t order,
    uint32_t *value
)
{
    uint8_t bytes[4] = {0U, 0U, 0U, 0U};

    if (data == NULL || value == NULL) {
        return EDGE_MODBUS_INVALID_ARGUMENT;
    }
    if (length < 4U) {
        return EDGE_MODBUS_TRUNCATED;
    }
    switch (order) {
    case EDGE_MODBUS_ORDER_ABCD:
        (void)memcpy(bytes, data, sizeof(bytes));
        break;
    case EDGE_MODBUS_ORDER_BADC:
        bytes[0] = data[1];
        bytes[1] = data[0];
        bytes[2] = data[3];
        bytes[3] = data[2];
        break;
    case EDGE_MODBUS_ORDER_CDAB:
        bytes[0] = data[2];
        bytes[1] = data[3];
        bytes[2] = data[0];
        bytes[3] = data[1];
        break;
    case EDGE_MODBUS_ORDER_DCBA:
        bytes[0] = data[3];
        bytes[1] = data[2];
        bytes[2] = data[1];
        bytes[3] = data[0];
        break;
    default:
        return EDGE_MODBUS_INVALID_ARGUMENT;
    }
    *value =
        ((uint32_t)bytes[0] << 24U)
        | ((uint32_t)bytes[1] << 16U)
        | ((uint32_t)bytes[2] << 8U)
        | (uint32_t)bytes[3];
    return EDGE_MODBUS_OK;
}

edge_modbus_result_t edge_modbus_decode_f32(
    const uint8_t *data,
    size_t length,
    edge_modbus_word_order_t order,
    float *value
)
{
    uint32_t encoded = 0U;
    edge_modbus_result_t result = EDGE_MODBUS_OK;

    if (value == NULL) {
        return EDGE_MODBUS_INVALID_ARGUMENT;
    }
    result = edge_modbus_decode_u32(data, length, order, &encoded);
    if (result != EDGE_MODBUS_OK) {
        return result;
    }
    (void)memcpy(value, &encoded, sizeof(encoded));
    return EDGE_MODBUS_OK;
}
