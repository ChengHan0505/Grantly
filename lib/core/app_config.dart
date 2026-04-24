class AppConfig {
  static const String environment = String.fromEnvironment('APP_ENV', defaultValue: 'dev');
  static const String backendBaseUrl =
      String.fromEnvironment('BACKEND_BASE_URL', defaultValue: 'http://localhost:8000');
  static const String aiSandboxBaseUrl =
      String.fromEnvironment('AI_SANDBOX_BASE_URL', defaultValue: 'http://localhost:8001');
}
