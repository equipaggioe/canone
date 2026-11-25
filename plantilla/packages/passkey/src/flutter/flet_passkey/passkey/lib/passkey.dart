/// The passkeys of the system, without a browser: Credential Manager on
/// Android, AuthenticationServices on iOS and macOS, and the WebAuthn API
/// on Windows.
///
/// The options and the response are the JSON of WebAuthn, as the server
/// sends and reads them.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart';

const _channel = MethodChannel('passkey');

/// Why a ceremony gave no credential.
enum PasskeyFailure {
  /// The user closed the sheet or the dialog of the system.
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
Future<String> getPasskey(String options) =>
    Platform.isWindows ? _windowsGet(options) : _call<String>('get', options);

/// Creates a passkey: [options] are those of `navigator.credentials.create()`.
Future<String> createPasskey(String options) =>
    Platform.isWindows ? _windowsCreate(options) : _call<String>('create', options);

Future<T> _call<T>(String method, Object arguments) async {
  try {
    final response = await _channel.invokeMethod<T>(method, arguments);
    if (response == null) {
      throw const PasskeyException(PasskeyFailure.failed, 'The system gave no response');
    }
    return response;
  } on PlatformException catch (error) {
    throw PasskeyException(PasskeyFailure.values.byName(error.code), error.message ?? '');
  }
}

Uint8List _bytes(Object? value) => base64Url.decode(base64Url.normalize(value! as String));

String _base64(Object? value) => base64Url.encode(value! as Uint8List).replaceAll('=', '');

List<Uint8List> _ids(Object? descriptors) => [
  for (final descriptor in (descriptors as List<Object?>?) ?? const [])
    _bytes((descriptor! as Map<String, Object?>)['id']),
];

// The API of Windows signs the clientDataJSON that the app writes, with
// the origin of the RP ID, as a browser on that domain would.
Uint8List _clientData(String type, Object? challenge, String rpId) => utf8.encode(
  jsonEncode({
    'type': type,
    'challenge': challenge,
    'origin': 'https://$rpId',
    'crossOrigin': false,
  }),
);

String _credential(Object? id, Map<String, Object?> response) => jsonEncode({
  'id': _base64(id),
  'rawId': _base64(id),
  'type': 'public-key',
  'response': response,
  'clientExtensionResults': <String, Object?>{},
  'authenticatorAttachment': 'platform',
});

Future<String> _windowsGet(String text) async {
  final options = jsonDecode(text) as Map<String, Object?>;
  final rpId = options['rpId']! as String;
  final clientData = _clientData('webauthn.get', options['challenge'], rpId);
  final result = await _call<Map<Object?, Object?>>('get', {
    'rpId': rpId,
    'clientData': clientData,
    'allowCredentials': _ids(options['allowCredentials']),
    'userVerification': options['userVerification'] ?? 'preferred',
  });
  return _credential(result['credentialId'], {
    'clientDataJSON': _base64(clientData),
    'authenticatorData': _base64(result['authenticatorData']),
    'signature': _base64(result['signature']),
    'userHandle': _base64(result['userHandle']),
  });
}

Future<String> _windowsCreate(String text) async {
  final options = jsonDecode(text) as Map<String, Object?>;
  final rp = options['rp']! as Map<String, Object?>;
  final user = options['user']! as Map<String, Object?>;
  final selection = options['authenticatorSelection'] as Map<String, Object?>? ?? const {};
  final rpId = rp['id']! as String;
  final clientData = _clientData('webauthn.create', options['challenge'], rpId);
  final result = await _call<Map<Object?, Object?>>('create', {
    'rpId': rpId,
    'rpName': rp['name']! as String,
    'userId': _bytes(user['id']),
    'userName': user['name']! as String,
    'userDisplayName': user['displayName'] as String? ?? '',
    'algorithms': [
      for (final parameter in options['pubKeyCredParams']! as List<Object?>)
        (parameter! as Map<String, Object?>)['alg']! as int,
    ],
    'excludeCredentials': _ids(options['excludeCredentials']),
    'clientData': clientData,
    'userVerification': selection['userVerification'] ?? 'preferred',
  });
  return _credential(result['credentialId'], {
    'clientDataJSON': _base64(clientData),
    'attestationObject': _base64(result['attestationObject']),
    'transports': result['transports'],
  });
}
