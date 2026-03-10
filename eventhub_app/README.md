# EventHub Flutter App

A cross-platform Flutter app that aggregates events from BookMyShow, Insider, and District into one unified event discovery interface.

## Project structure

```text
eventhub_app/
├── pubspec.yaml
└── lib/
    ├── main.dart
    ├── models/
    │   └── event.dart
    ├── services/
    │   └── api_service.dart
    ├── screens/
    │   ├── home_screen.dart
    │   └── event_detail_screen.dart
    ├── widgets/
    │   └── event_card.dart
    └── utils/
        └── constants.dart
```

## Run locally

```bash
cd eventhub_app
flutter pub get
flutter run
```

## API

The app fetches data from:

`GET https://api.eventhub.com/events`

Expected payload:

```json
[
  {
    "title": "Coldplay Tribute Night",
    "platform": "BookMyShow",
    "date": "2026-03-21",
    "location": "Mumbai",
    "price": "₹1200",
    "url": "https://bookmyshow.com/event",
    "image": "https://image-url"
  }
]
```
