#include "edge/update_manifest.h"

#include <ctype.h>
#include <string.h>

static bool edge_bounded_string_valid(
    const char *value,
    size_t capacity,
    bool version
)
{
    size_t index = 0U;

    if (value == NULL || value[0] == '\0') {
        return false;
    }
    for (index = 0U; index < capacity; ++index) {
        const unsigned char character = (unsigned char)value[index];
        if (character == '\0') {
            return true;
        }
        if (
            isalnum(character) == 0
            && character != (unsigned char)'.'
            && character != (unsigned char)'-'
            && (!version || character != (unsigned char)'+')
        ) {
            return false;
        }
    }
    return false;
}

edge_update_result_t edge_update_manifest_validate(
    const edge_update_manifest_t *manifest,
    const char *expected_target,
    uint32_t maximum_image_size,
    uint32_t installed_security_counter,
    edge_signature_verify_fn verify_signature,
    void *verify_context
)
{
    size_t index = 0U;
    bool digest_nonzero = false;

    if (
        manifest == NULL
        || expected_target == NULL
        || verify_signature == NULL
        || maximum_image_size == 0U
    ) {
        return EDGE_UPDATE_INVALID_ARGUMENT;
    }
    if (
        !edge_bounded_string_valid(
            manifest->target,
            sizeof(manifest->target),
            false
        )
        || strncmp(
            manifest->target,
            expected_target,
            sizeof(manifest->target)
        ) != 0
    ) {
        return EDGE_UPDATE_WRONG_TARGET;
    }
    if (!edge_bounded_string_valid(
            manifest->version,
            sizeof(manifest->version),
            true
        )) {
        return EDGE_UPDATE_INVALID_VERSION;
    }
    if (
        manifest->image_size == 0U
        || manifest->image_size > maximum_image_size
    ) {
        return EDGE_UPDATE_INVALID_SIZE;
    }
    if (manifest->security_counter <= installed_security_counter) {
        return EDGE_UPDATE_ROLLBACK_REJECTED;
    }
    for (index = 0U; index < sizeof(manifest->image_sha256); ++index) {
        digest_nonzero = digest_nonzero || manifest->image_sha256[index] != 0U;
    }
    if (!digest_nonzero) {
        return EDGE_UPDATE_INVALID_DIGEST;
    }
    if (
        manifest->signature_length == 0U
        || manifest->signature_length > sizeof(manifest->signature)
        || !verify_signature(manifest, verify_context)
    ) {
        return EDGE_UPDATE_INVALID_SIGNATURE;
    }
    return EDGE_UPDATE_OK;
}
