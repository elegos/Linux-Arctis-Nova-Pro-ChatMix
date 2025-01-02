from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QMainWindow,
                             QSlider, QStackedWidget, QVBoxLayout, QWidget)

from arctis_chatmix.custom_widgets.q_toggle import QToggle
from arctis_chatmix.translations import Translations


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(Translations.get_instance().get_translation('app', 'settings_window_title'))

        # Set the minimum size and adjust to screen geometry
        self.setMinimumSize(800, 600)
        available_geometry = self.screen().availableGeometry()
        self.resize(min(800, available_geometry.width()), min(600, available_geometry.height()))

        # TODO make this dynamic (init, translations)
        sections = {
            'Microphone': {
                'Volume': {'type': 'slider', 'configuration': {'min': 0x01, 'max': 0x10, 'step': 1, 'default_value': 0x10, 'min_label': 'Muted', 'max_label': '100%'}},
                'Gain': {'type': 'toggle', 'configuration': {'off_label': 'Low', 'on_label': 'High', 'toggled': True}},
                'Side tone': {'type': 'slider', 'configuration': {'min': 0x00, 'max': 0x03, 'step': 1, 'default_value': 0x00, 'min_label': 'None', 'max_label': 'high'}},
            },
            'Active Noise Cancelling': {
                'Level': {'type': 'slider', 'configuration': {'min': 0x00, 'max': 0x03, 'step': 1, 'default_value': 0x00, 'min_label': 'Disabled', 'max_label': 'High'}},
            },
            'Power Management': {
                'Shutdown after': {'type': 'slider', 'configuration': {'min': 0x00, 'max': 0x06, 'step': 1, 'default_value': 0x04, 'min_label': 'Disabled', 'max_label': '60 minutes'}},
            },
            'Wireless': {
                'Wireless mode': {'type': 'toggle', 'configuration': {'off_label': 'Speed', 'on_label': 'Range', 'toggled': False}},
            }
        }

        # Create a list widget for sections on the left
        section_list = QListWidget()
        section_list.addItems(sections.keys())
        section_list.setFixedWidth(max(section_list.sizeHintForColumn(0), 200))
        section_list.currentRowChanged.connect(self.change_panel)

        # Create a stacked widget for panels on the right
        panel_stack = QStackedWidget()

        def test_callback(*args, **kwargs):
            print(args, kwargs)

        # Create and add panels to the stacked widget
        for settings in sections.values():
            panel = QWidget()
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            for setting, options in settings.items():
                widget = QWidget()
                w_layout = QHBoxLayout()
                widget.setLayout(w_layout)
                w_layout.addWidget(QLabel(f'{setting}: '))

                widget: QWidget = None
                if options['type'] == 'slider':
                    config = options['configuration']
                    widget = self.get_slider_configuration_widget(
                        setting, config['min'], config['max'], config['step'],
                        config['default_value'], config['min_label'], config['max_label'],
                        test_callback,
                    )
                elif options['type'] == 'toggle':
                    config = options['configuration']
                    widget = self.get_checkbox_configuration_widget(
                        setting, config['off_label'], config['on_label'], config['toggled'],
                        test_callback,
                    )

                if widget is not None:
                    layout.addWidget(widget)
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
        self, name: str, min: int, max: int, step: int, default_value: int, min_label: str, max_label: str, on_value_changed: Optional[Callable[[int], None]]
    ) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)

        controller = QSlider(orientation=Qt.Orientation.Horizontal)
        controller.setMinimum(min)
        controller.setMaximum(max)
        controller.setSingleStep(step)
        controller.setValue(default_value)

        layout.addWidget(QLabel(f'{name}: '))
        layout.addWidget(QLabel(min_label))
        layout.addWidget(controller)
        layout.addWidget(QLabel(max_label))

        if on_value_changed is not None:
            controller.sliderReleased.connect(lambda: on_value_changed(controller.value()))

        return widget

    def get_checkbox_configuration_widget(
        self, name: str, off_label: str, on_label: str, toggled: bool, on_value_changed: Optional[Callable[[int], None]]
    ):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        widget.setLayout(layout)

        controller = QToggle()
        controller.setChecked(toggled)

        layout.addWidget(QLabel(f'{name}: '))
        layout.addWidget(QLabel(off_label))
        layout.addWidget(controller)
        layout.addWidget(QLabel(on_label))

        if on_value_changed is not None:
            controller.stateChanged.connect(lambda: on_value_changed(controller.isChecked()))

        return widget
