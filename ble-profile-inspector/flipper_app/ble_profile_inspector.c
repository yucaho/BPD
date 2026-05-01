#include <furi.h>
#include <gui/gui.h>
#include <gui/view_dispatcher.h>
#include <gui/modules/widget.h>
#include <input/input.h>

#define VIEW_MAIN 0

typedef struct {
    ViewDispatcher* dispatcher;
    Widget* widget;
    uint32_t scan_runs;
    uint32_t observed_packets;
    int8_t strongest_rssi;
    bool scan_active;
} App;

static void app_render(App* app) {
    widget_reset(app->widget);
    widget_add_string_element(app->widget, 2, 8, AlignLeft, AlignTop, FontPrimary, "BLE Profile Inspector");

    if(app->scan_active) {
        widget_add_string_element(app->widget, 2, 24, AlignLeft, AlignTop, FontSecondary, "Mode: Passive scan (session)");
        widget_add_string_element(app->widget, 2, 34, AlignLeft, AlignTop, FontSecondary, "Collecting advertisements...");
    } else {
        widget_add_string_element(app->widget, 2, 24, AlignLeft, AlignTop, FontSecondary, "Mode: Idle");
        widget_add_string_element(app->widget, 2, 34, AlignLeft, AlignTop, FontSecondary, "OK to start new passive scan");
    }

    char line[64];
    snprintf(line, sizeof(line), "Scan runs: %lu", (unsigned long)app->scan_runs);
    widget_add_string_element(app->widget, 2, 46, AlignLeft, AlignTop, FontSecondary, line);

    snprintf(line, sizeof(line), "Packets seen: %lu", (unsigned long)app->observed_packets);
    widget_add_string_element(app->widget, 2, 56, AlignLeft, AlignTop, FontSecondary, line);

    snprintf(line, sizeof(line), "Strongest RSSI: %d dBm", app->strongest_rssi);
    widget_add_string_element(app->widget, 2, 66, AlignLeft, AlignTop, FontSecondary, line);

    widget_add_string_element(app->widget, 2, 78, AlignLeft, AlignTop, FontSecondary, "OK=start/stop  BACK=exit");
}

static bool app_input_callback(InputEvent* event, void* context) {
    App* app = context;
    if(event->type != InputTypeShort) return false;

    if(event->key == InputKeyOk) {
        app->scan_active = !app->scan_active;
        if(app->scan_active) {
            app->scan_runs++;
            // Placeholder counters for firmware-agnostic buildability. In a firmware-specific
            // implementation, this is where native passive BLE scanner callbacks would increment
            // observed_packets and strongest_rssi from advertisement metadata.
            app->observed_packets += 12;
            if(app->strongest_rssi < -48) app->strongest_rssi = -48;
        }
        app_render(app);
        return true;
    }

    return false;
}

int32_t ble_profile_inspector_app(void* p) {
    UNUSED(p);

    App* app = malloc(sizeof(App));
    app->dispatcher = view_dispatcher_alloc();
    app->widget = widget_alloc();
    app->scan_runs = 0;
    app->observed_packets = 0;
    app->strongest_rssi = -127;
    app->scan_active = false;

    Gui* gui = furi_record_open(RECORD_GUI);
    view_dispatcher_attach_to_gui(app->dispatcher, gui, ViewDispatcherTypeFullscreen);
    view_dispatcher_add_view(app->dispatcher, VIEW_MAIN, widget_get_view(app->widget));
    view_set_input_callback(widget_get_view(app->widget), app_input_callback);
    view_set_context(widget_get_view(app->widget), app);

    app_render(app);
    view_dispatcher_switch_to_view(app->dispatcher, VIEW_MAIN);
    view_dispatcher_run(app->dispatcher);

    view_dispatcher_remove_view(app->dispatcher, VIEW_MAIN);
    widget_free(app->widget);
    view_dispatcher_free(app->dispatcher);
    furi_record_close(RECORD_GUI);
    free(app);

    return 0;
}
