class Event {
  final String title;
  final String platform;
  final String date;
  final String location;
  final String price;
  final String url;
  final String image;

  const Event({
    required this.title,
    required this.platform,
    required this.date,
    required this.location,
    required this.price,
    required this.url,
    required this.image,
  });

  factory Event.fromJson(Map<String, dynamic> json) {
    return Event(
      title: json['title']?.toString() ?? 'Untitled Event',
      platform: json['platform']?.toString() ?? 'Unknown',
      date: json['date']?.toString() ?? 'TBA',
      location: json['location']?.toString() ?? 'Unknown',
      price: json['price']?.toString() ?? 'N/A',
      url: json['url']?.toString() ?? '',
      image: json['image']?.toString() ??
          'https://placehold.co/800x450?text=EventHub',
    );
  }
}
