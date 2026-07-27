#ifndef EDGE_MODBUS_CRC_H
#define EDGE_MODBUS_CRC_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

uint16_t edge_modbus_crc16(const uint8_t *data, size_t length);

#ifdef __cplusplus
}
#endif

#endif
