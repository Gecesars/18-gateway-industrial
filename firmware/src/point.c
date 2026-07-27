#include "edge/point.h"

#include <ctype.h>

bool edge_point_is_good(const edge_point_record_t *point)
{
    return point != NULL && point->quality == EDGE_QUALITY_GOOD;
}

bool edge_point_has_quality(
    const edge_point_record_t *point,
    edge_quality_t flag
)
{
    return point != NULL && (point->quality & flag) == flag;
}

void edge_point_add_quality(edge_point_record_t *point, edge_quality_t flag)
{
    if (point != NULL) {
        point->quality |= flag;
    }
}

void edge_point_clear_quality(edge_point_record_t *point, edge_quality_t flag)
{
    if (point != NULL) {
        point->quality &= ~flag;
    }
}

bool edge_point_identifier_is_valid(const char *identifier, size_t capacity)
{
    size_t index = 0U;

    if (identifier == NULL || capacity < 2U || identifier[0] == '\0') {
        return false;
    }

    while (index < capacity && identifier[index] != '\0') {
        const unsigned char character = (unsigned char)identifier[index];
        const bool allowed =
            isalnum(character) != 0 ||
            character == (unsigned char)'.' ||
            character == (unsigned char)'_' ||
            character == (unsigned char)'-';

        if (!allowed) {
            return false;
        }
        ++index;
    }

    return index > 0U && index < capacity;
}
