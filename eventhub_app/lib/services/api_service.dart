import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/event.dart';
import '../utils/constants.dart';

class ApiService {
  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  Future<List<Event>> fetchEvents() async {
    final response = await _client.get(Uri.parse(AppConstants.eventsEndpoint));

    if (response.statusCode != 200) {
      throw Exception('Failed to load events. Please try again.');
    }

    final List<dynamic> decoded = jsonDecode(response.body) as List<dynamic>;
    return decoded
        .map((item) => Event.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
