#ifndef EDGE_UPDATE_MANIFEST_H
#define EDGE_UPDATE_MANIFEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EDGE_UPDATE_VERSION_CAPACITY 24U
#define EDGE_UPDATE_TARGET_CAPACITY 32U
#define EDGE_UPDATE_SHA256_SIZE 32U
#define EDGE_UPDATE_SIGNATURE_MAX 96U

typedef struct {
    char target[EDGE_UPDATE_TARGET_CAPACITY];
    char version[EDGE_UPDATE_VERSION_CAPACITY];
    uint32_t security_counter;
    uint32_t image_size;
    uint8_t image_sha256[EDGE_UPDATE_SHA256_SIZE];
    uint8_t signature[EDGE_UPDATE_SIGNATURE_MAX];
    size_t signature_length;
} edge_update_manifest_t;

typedef bool (*edge_signature_verify_fn)(
    const edge_update_manifest_t *manifest,
    void *context
);

typedef enum {
    EDGE_UPDATE_OK = 0,
    EDGE_UPDATE_INVALID_ARGUMENT,
    EDGE_UPDATE_WRONG_TARGET,
    EDGE_UPDATE_INVALID_VERSION,
    EDGE_UPDATE_INVALID_SIZE,
    EDGE_UPDATE_ROLLBACK_REJECTED,
    EDGE_UPDATE_INVALID_DIGEST,
    EDGE_UPDATE_INVALID_SIGNATURE
} edge_update_result_t;

edge_update_result_t edge_update_manifest_validate(
    const edge_update_manifest_t *manifest,
    const char *expected_target,
    uint32_t maximum_image_size,
    uint32_t installed_security_counter,
    edge_signature_verify_fn verify_signature,
    void *verify_context
);

#ifdef __cplusplus
}
#endif

#endif
