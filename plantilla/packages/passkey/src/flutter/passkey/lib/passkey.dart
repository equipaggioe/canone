/// The passkeys of the system: Credential Manager on Android and
/// AuthenticationServices on iOS, without a browser.
///
/// The options and the response are the JSON of WebAuthn, as the server
/// sends and reads them.
library;

import 'package:flutter/services.dart';

const _channel = MethodChannel('passkey');

/// Why a ceremony gave no credential.
enum PasskeyFailure {
  /// The user closed the sheet of the system.
  cancelled,

  /// The device has no passkey for the server.
  noCredential,

  /// The device or its provider does not offer passkeys.
  unsupported,

  /// Anything else; the message says what.
  failed,
}

/// A ceremony that gave no credential.
class PasskeyException implements Exception {
  const PasskeyException(this.failure, this.message);

  final PasskeyFailure failure;
  final String message;

  @override
  String toString() => 'PasskeyException(${failure.name}): $message';
}

/// Signs in: [options] are those of `navigator.credentials.get()`.
Future<String> getPasskey(String options) => _call('get', options);

/// Creates a passkey: [options] are those of `navigator.credentials.create()`.
Future<String> createPasskey(String options) => _call('create', options);

Future<String> _call(String method, String options) async {
  try {
    final response = await _channel.invokeMethod<String>(method, options);
    if (response == null) {
      throw const PasskeyException(PasskeyFailure.failed, 'The system gave no response');
    }
    return response;
  } on PlatformException catch (error) {
    throw PasskeyException(PasskeyFailure.values.byName(error.code), error.message ?? '');
  }
}
