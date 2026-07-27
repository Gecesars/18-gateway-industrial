#ifndef EDGE_STATE_MACHINE_H
#define EDGE_STATE_MACHINE_H

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    EDGE_STATE_BOOT = 0,
    EDGE_STATE_SELF_TEST,
    EDGE_STATE_PROVISIONING,
    EDGE_STATE_CONNECTING,
    EDGE_STATE_RUNNING,
    EDGE_STATE_DEGRADED,
    EDGE_STATE_UPDATING,
    EDGE_STATE_FAULT
} edge_state_t;

typedef enum {
    EDGE_EVENT_BOOT_COMPLETE = 0,
    EDGE_EVENT_SELF_TEST_OK,
    EDGE_EVENT_SELF_TEST_FAILED,
    EDGE_EVENT_CONFIG_AVAILABLE,
    EDGE_EVENT_NETWORK_READY,
    EDGE_EVENT_NETWORK_LOST,
    EDGE_EVENT_CRITICAL_DEGRADED,
    EDGE_EVENT_RECOVERED,
    EDGE_EVENT_UPDATE_REQUESTED,
    EDGE_EVENT_UPDATE_FINISHED,
    EDGE_EVENT_UPDATE_FAILED,
    EDGE_EVENT_FACTORY_RESET
} edge_event_t;

typedef struct {
    edge_state_t state;
    edge_state_t state_before_update;
    unsigned long transition_count;
} edge_state_machine_t;

void edge_state_machine_init(edge_state_machine_t *machine);
int edge_state_machine_dispatch(
    edge_state_machine_t *machine,
    edge_event_t event
);
const char *edge_state_name(edge_state_t state);

#ifdef __cplusplus
}
#endif

#endif
