from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QFormLayout, QHBoxLayout, QLabel, QLayout,
                             QListWidget, QMainWindow, QSlider, QStackedWidget,
                             QWidget)

from arctis_chatmix.custom_widgets.q_toggle import QToggle
from arctis_chatmix.device_manager.device_settings import DeviceSetting, SliderSetting, ToggleSetting
from arctis_chatmix.qt_utils import get_icon_pixmap
from arctis_chatmix.translations import Translations


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(Translations.get_instance().get_translation('app', 'settings_window_title'))
        # Note: Wayland does not support window icons (yet?)
        self.setWindowIcon(QIcon(get_icon_pixmap()))

        # Set the minimum size and adjust to screen geometry
        self.setMinimumSize(800, 600)
        available_geometry = self.screen().availableGeometry()
        self.resize(min(800, available_geometry.width()), min(600, available_geometry.height()))

        def test_callback(*args, **kwargs):
            print(args, kwargs)

        # TODO make this dynamic (init, translations)
        sections: dict[str, list[DeviceSetting]] = {
            'Microphone': [
                SliderSetting('mic_volume', 'mic_volume_muted', 'mic_volume_max', 0x01, 0x10, 1, 0x10, test_callback),
                SliderSetting('mic_side_tone', 'mic_side_tone_none', 'mic_side_tone_high', 0x00, 0x03, 1, 0x00, test_callback),
                ToggleSetting('mic_gain', 'mic_gain_low', 'mic_gain_high', True, test_callback),
            ],
            'Active Noise Cancelling': [
                SliderSetting('anc_level', 'anc_level_low', 'anc_level_high', 0x00, 0x03, 1, 0x00, test_callback),
            ],
            'Power Management': [
                SliderSetting('pm_shutdown', 'pm_shutdown_disabled', 'pm_shutdown_60_minutes', 0x00, 0x06, 1, 0x04, test_callback),
            ],
            'Wireless': [
                ToggleSetting('wireless_mode', 'wireless_mode_speed', 'wireless_mode_range', False, test_callback),
            ],
        }

        # Create a list widget for sections on the left
        section_list = QListWidget()
        section_list.addItems(sections.keys())
        section_list.setFixedWidth(max(section_list.sizeHintForColumn(0), 200))
        section_list.currentRowChanged.connect(self.change_panel)

        # Create a stacked widget for panels on the right
        panel_stack = QStackedWidget()

        # Create and add panels to the stacked widget
        for settings in sections.values():
            panel = QWidget()
            layout = QFormLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            for setting in settings:
                widget_layout = QWidget()
                w_layout = QHBoxLayout()
                widget_layout.setLayout(w_layout)
                w_layout.addWidget(QLabel(f'{setting.name}: '))

                widget_layout: QLayout = None

                if isinstance(setting, SliderSetting):
                    widget_layout = self.get_slider_configuration_widget(
                        setting.min_value, setting.max_value, setting.step,
                        setting.current_state, setting.min_label, setting.max_label,
                        setting.on_value_change
                    )
                elif isinstance(setting, ToggleSetting):
                    widget_layout = self.get_checkbox_configuration_widget(
                        setting.untoggled_label, setting.toggled_label, setting.current_state,
                        setting.on_value_change
                    )

                if widget_layout is not None:
                    layout.addRow(setting.name, widget_layout)
            panel.setLayout(layout)

            panel_stack.addWidget(panel)

        # Create a central widget and set up the layout
        central_widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(section_list)
        layout.addWidget(panel_stack)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def change_panel(self, index):
        # Change the panel based on the selected section
        self.centralWidget().findChild(QStackedWidget).setCurrentIndex(index)

    def get_slider_configuration_widget(
        self, min: int, max: int, step: int, default_value: int, min_label: str, max_label: str, on_value_changed: Optional[Callable[[int], None]]
    ) -> QLayout:
        layout = QHBoxLayout()

        controller = QSlider(orientation=Qt.Orientation.Horizontal)
        controller.setMinimum(min)
        controller.setMaximum(max)
        controller.setSingleStep(step)
        controller.setValue(default_value)

        # layout.addWidget(QLabel(f'{name}: '))
        layout.addWidget(QLabel(min_label))
        layout.addWidget(controller)
        layout.addWidget(QLabel(max_label))

        if on_value_changed is not None:
            controller.sliderReleased.connect(lambda: on_value_changed(controller.value()))

        return layout

    def get_checkbox_configuration_widget(
        self, off_label: str, on_label: str, toggled: bool, on_value_changed: Optional[Callable[[int], None]]
    ) -> QLayout:
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        controller = QToggle()
        controller.setChecked(toggled)

        layout.addWidget(QLabel(off_label))
        layout.addWidget(controller)
        layout.addWidget(QLabel(on_label))

        if on_value_changed is not None:
            controller.stateChanged.connect(lambda: on_value_changed(controller.isChecked()))

        return layout