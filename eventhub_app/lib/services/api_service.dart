import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/event.dart';
import '../utils/constants.dart';

/// Handles all event API communication.
///
/// If the remote API is unavailable, we return local fallback data so the app
/// still works during development and demos.
class ApiService {
  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  Future<List<Event>> fetchEvents() async {
    try {
      final response = await _client
          .get(Uri.parse(AppConstants.eventsEndpoint))
          .timeout(const Duration(seconds: 12));

      if (response.statusCode != 200) {
        throw Exception('Unexpected status code: ${response.statusCode}');
      }

      final dynamic decoded = jsonDecode(response.body);

      // Accept either a list payload or an object wrapping the list.
      final List<dynamic> rawEvents = switch (decoded) {
        List<dynamic> list => list,
        Map<String, dynamic> map when map['events'] is List<dynamic> =>
          map['events'] as List<dynamic>,
        _ => <dynamic>[]
      };

      final events = rawEvents
          .whereType<Map<String, dynamic>>()
          .map(Event.fromJson)
          .toList();

      // Keep UI functional even if backend returns an empty list.
      return events.isEmpty ? _fallbackEvents : events;
    } on TimeoutException {
      return _fallbackEvents;
    } catch (_) {
      return _fallbackEvents;
    }
  }

  List<Event> get _fallbackEvents => const [
        Event(
          title: 'Coldplay Tribute Night',
          platform: 'BookMyShow',
          date: '2026-03-21',
          location: 'Mumbai',
          price: '₹1200',
          url: 'https://in.bookmyshow.com/explore/events-mumbai',
          image: 'https://placehold.co/800x450?text=Coldplay+Tribute',
        ),
        Event(
          title: 'Startup Mixer 2026',
          platform: 'District',
          date: '2026-04-05',
          location: 'Bengaluru',
          price: '₹499',
          url: 'https://district.in/',
          image: 'https://placehold.co/800x450?text=Startup+Mixer',
        ),
        Event(
          title: 'Indie Art Weekend',
          platform: 'Insider',
          date: '2026-04-12',
          location: 'Delhi',
          price: 'Free',
          url: 'https://insider.in/all-events-in-delhi',
          image: 'https://placehold.co/800x450?text=Indie+Art+Weekend',
        ),
      ];
}
