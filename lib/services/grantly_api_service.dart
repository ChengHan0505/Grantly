import 'dart:convert';

import 'package:http/http.dart' as http;

import '../core/app_config.dart';

class GrantlyApiService {
  GrantlyApiService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Uri _backendUri(String path) => Uri.parse('${AppConfig.backendBaseUrl}$path');
  Uri _sandboxUri(String path) => Uri.parse('${AppConfig.aiSandboxBaseUrl}$path');

  Future<Map<String, dynamic>> healthCheck() async {
    final response = await _client.get(_backendUri('/'));
    _ensureOk(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> createUser({
    required String username,
    required String email,
    String? externalAuthId,
  }) async {
    final response = await _client.post(
      _backendUri('/users'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'external_auth_id': externalAuthId,
      }),
    );
    _ensureOk(response, acceptedCodes: {201});
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<List<dynamic>> rankedGrants(int userId) async {
    final response = await _client.get(_backendUri('/grants/match/$userId'));
    _ensureOk(response);
    return jsonDecode(response.body) as List<dynamic>;
  }

  // Optional bridge endpoint if ai_sandbox is exposed as a local API process.
  Future<Map<String, dynamic>> aiSandboxPing() async {
    final response = await _client.get(_sandboxUri('/health'));
    _ensureOk(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  void _ensureOk(http.Response response, {Set<int> acceptedCodes = const {200}}) {
    if (!acceptedCodes.contains(response.statusCode)) {
      throw Exception('API error ${response.statusCode}: ${response.body}');
    }
  }
}
