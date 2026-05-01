#include <furi.h>
#include <gui/gui.h>
#include <gui/view_dispatcher.h>
#include <gui/modules/widget.h>
#include <input/input.h>

#define VIEW_MAIN 0
#define MAX_AD_BOXES 3

typedef struct {
    const char* name;
    int8_t rssi;
    const char* service;
} AdSummary;

typedef struct {
    ViewDispatcher* dispatcher;
    Widget* widget;
    uint32_t scan_runs;
    uint32_t active_advertisements;
    bool scan_active;
    AdSummary ads[MAX_AD_BOXES];
} App;

static void app_mock_refresh_ads(App* app) {
    // Firmware-agnostic placeholder data. Replace with native BLE advertisement callback data.
    app->active_advertisements = 3;
    app->ads[0] = (AdSummary){.name = "Tag Sensor", .rssi = -54, .service = "180F"};
    app->ads[1] = (AdSummary){.name = "Beacon Node", .rssi = -67, .service = "FEAA"};
    app->ads[2] = (AdSummary){.name = "Dev Kit", .rssi = -72, .service = "1234"};
}

static void app_clear_ads(App* app) {
    app->active_advertisements = 0;
    for(size_t i = 0; i < MAX_AD_BOXES; i++) {
        app->ads[i] = (AdSummary){.name = "-", .rssi = 0, .service = "-"};
    }
}

static void app_render(App* app) {
    widget_reset(app->widget);
    widget_add_string_element(app->widget, 2, 2, AlignLeft, AlignTop, FontPrimary, "BLE Profile Inspector");

    if(app->scan_active) {
        widget_add_string_element(app->widget, 2, 14, AlignLeft, AlignTop, FontSecondary, "Status: Scanning");
    } else {
        widget_add_string_element(app->widget, 2, 14, AlignLeft, AlignTop, FontSecondary, "Status: Idle");
    }

    char line[64];
    snprintf(line, sizeof(line), "Runs:%lu  Active Ads:%lu", (unsigned long)app->scan_runs, (unsigned long)app->active_advertisements);
    widget_add_string_element(app->widget, 2, 24, AlignLeft, AlignTop, FontSecondary, line);

    uint8_t y = 34;
    for(size_t i = 0; i < MAX_AD_BOXES; i++) {
        snprintf(line, sizeof(line), "[%lu] %s", (unsigned long)(i + 1), app->ads[i].name);
        widget_add_string_element(app->widget, 2, y, AlignLeft, AlignTop, FontSecondary, line);
        snprintf(line, sizeof(line), " RSSI:%d  SVC:%s", app->ads[i].rssi, app->ads[i].service);
        widget_add_string_element(app->widget, 2, y + 8, AlignLeft, AlignTop, FontSecondary, line);
        y += 16;
    }

    if(app->scan_active) {
        widget_add_string_element(app->widget, 2, 84, AlignLeft, AlignTop, FontSecondary, "BACK=stop scan");
    } else {
        widget_add_string_element(app->widget, 2, 84, AlignLeft, AlignTop, FontSecondary, "BACK=exit");
    }
    widget_add_string_element(app->widget, 2, 92, AlignLeft, AlignTop, FontSecondary, "OK=start scan");
}

static bool app_input_callback(InputEvent* event, void* context) {
    App* app = context;
    if(event->type != InputTypeShort) return false;

    if(event->key == InputKeyOk) {
        app->scan_active = true;
        app->scan_runs++;
        app_mock_refresh_ads(app);
        app_render(app);
        return true;
    }

    if(event->key == InputKeyBack) {
        if(app->scan_active) {
            app->scan_active = false;
            app_clear_ads(app);
            app_render(app);
            return true;
        }
        view_dispatcher_stop(app->dispatcher);
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
    app->scan_active = false;
    app_clear_ads(app);

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
