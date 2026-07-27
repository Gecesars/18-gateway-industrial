#include "edge/state_machine.h"

#include <stddef.h>

void edge_state_machine_init(edge_state_machine_t *machine)
{
    if (machine != NULL) {
        machine->state = EDGE_STATE_BOOT;
        machine->state_before_update = EDGE_STATE_BOOT;
        machine->transition_count = 0UL;
    }
}

static int edge_state_change(
    edge_state_machine_t *machine,
    edge_state_t state
)
{
    if (machine->state == state) {
        return 1;
    }
    machine->state = state;
    ++machine->transition_count;
    return 1;
}

int edge_state_machine_dispatch(
    edge_state_machine_t *machine,
    edge_event_t event
)
{
    if (machine == NULL) {
        return 0;
    }
    if (event == EDGE_EVENT_FACTORY_RESET) {
        return edge_state_change(machine, EDGE_STATE_PROVISIONING);
    }
    if (
        event == EDGE_EVENT_UPDATE_REQUESTED
        && (machine->state == EDGE_STATE_RUNNING
            || machine->state == EDGE_STATE_DEGRADED)
    ) {
        machine->state_before_update = machine->state;
        return edge_state_change(machine, EDGE_STATE_UPDATING);
    }

    switch (machine->state) {
    case EDGE_STATE_BOOT:
        return event == EDGE_EVENT_BOOT_COMPLETE
            ? edge_state_change(machine, EDGE_STATE_SELF_TEST)
            : 0;
    case EDGE_STATE_SELF_TEST:
        if (event == EDGE_EVENT_SELF_TEST_OK) {
            return edge_state_change(machine, EDGE_STATE_PROVISIONING);
        }
        return event == EDGE_EVENT_SELF_TEST_FAILED
            ? edge_state_change(machine, EDGE_STATE_FAULT)
            : 0;
    case EDGE_STATE_PROVISIONING:
        return event == EDGE_EVENT_CONFIG_AVAILABLE
            ? edge_state_change(machine, EDGE_STATE_CONNECTING)
            : 0;
    case EDGE_STATE_CONNECTING:
        return event == EDGE_EVENT_NETWORK_READY
            ? edge_state_change(machine, EDGE_STATE_RUNNING)
            : 0;
    case EDGE_STATE_RUNNING:
        if (
            event == EDGE_EVENT_NETWORK_LOST
            || event == EDGE_EVENT_CRITICAL_DEGRADED
        ) {
            return edge_state_change(machine, EDGE_STATE_DEGRADED);
        }
        return 0;
    case EDGE_STATE_DEGRADED:
        return event == EDGE_EVENT_RECOVERED
            ? edge_state_change(machine, EDGE_STATE_RUNNING)
            : 0;
    case EDGE_STATE_UPDATING:
        if (event == EDGE_EVENT_UPDATE_FINISHED) {
            return edge_state_change(machine, EDGE_STATE_BOOT);
        }
        return event == EDGE_EVENT_UPDATE_FAILED
            ? edge_state_change(machine, machine->state_before_update)
            : 0;
    case EDGE_STATE_FAULT:
        return 0;
    default:
        return 0;
    }
}

const char *edge_state_name(edge_state_t state)
{
    static const char *const names[] = {
        "boot",
        "self-test",
        "provisioning",
        "connecting",
        "running",
        "degraded",
        "updating",
        "fault"
    };

    if ((unsigned int)state >= sizeof(names) / sizeof(names[0])) {
        return "invalid";
    }
    return names[state];
}
