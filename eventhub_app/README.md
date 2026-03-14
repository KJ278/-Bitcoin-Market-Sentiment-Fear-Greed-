# EventHub Flutter App

EventHub is a cross-platform Flutter app that aggregates events from BookMyShow, Insider, and District in one unified discovery interface.

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

## What is implemented

- Clean architecture split: UI layer (`screens/`, `widgets/`) and data layer (`services/`, `models/`).
- Home screen with loading state, pull-to-refresh, and scrollable event cards.
- Event detail screen with ticket link button.
- REST integration using `http` package.
- URL opening using `url_launcher`.
- Fallback sample events if API is unavailable, so the app remains usable.

## API endpoint

The app calls:

`GET https://api.eventhub.com/events`

Supported response shapes:

1. Raw list:

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

2. Wrapped list:

```json
{
  "events": [
    { "title": "..." }
  ]
}
```

## How to run

```bash
cd eventhub_app
flutter pub get
flutter run
```

## If you see errors

1. Make sure Flutter SDK is installed and available in PATH (`flutter --version`).
2. Run `flutter doctor` and fix any platform setup issues.
3. If `https://api.eventhub.com/events` is unreachable, the app will show fallback sample events.
4. For Android, ensure internet permission is present in your app template (`android.permission.INTERNET`), which is included by default in most Flutter templates.
