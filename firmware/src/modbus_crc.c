#include "edge/modbus_crc.h"

uint16_t edge_modbus_crc16(const uint8_t *data, size_t length)
{
    uint16_t crc = UINT16_C(0xFFFF);
    size_t index = 0U;

    if (data == NULL && length > 0U) {
        return 0U;
    }

    for (index = 0U; index < length; ++index) {
        unsigned int bit = 0U;
        crc ^= (uint16_t)data[index];

        for (bit = 0U; bit < 8U; ++bit) {
            const bool least_significant_bit = (crc & 1U) != 0U;
            crc >>= 1U;
            if (least_significant_bit) {
                crc ^= UINT16_C(0xA001);
            }
        }
    }

    return crc;
}
